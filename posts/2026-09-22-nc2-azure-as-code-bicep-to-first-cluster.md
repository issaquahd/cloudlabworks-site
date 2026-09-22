---
title: "NC2 on Azure, as code: Bicep for the landing zone, the NC2 v2 API for the organization, the cloud account and the cluster"
date: 2026-09-22
time: 07:00
by: Alex Alvord
slug: nc2-azure-as-code-bicep-to-first-cluster
section: nutanix
summary: The Azure twin of yesterday's AWS walkthrough, with one difference that matters: on Azure the NC2 console never has to be clicked. Bicep builds the tenant side (custom role, app registration, the three VNets with their delegated subnets, NAT gateways, peering, Route Server), and the NC2 v2 API creates the organization, the cloud account and the cluster with Prism Central and Flow Gateways inside it. ASCII at every step; OpenTofu on the v4 APIs takes over where yesterday's post did.
---

Yesterday's post had two halves: the NC2 console by hand, then OpenTofu against Prism Central. The Azure version can be one half. Everything the console does, the NC2 v2 API also does, including creating the organization, and everything Azure needs is a Bicep deployment. So this is the same walk, with the mouse taken away: Bicep for the tenant, four API calls for NC2, and the same OpenTofu files as yesterday for what comes after. Everything below is from the public NC2 on Azure Deployment and User Guide, the NC2 v2 API reference on nutanix.dev, and the Bicep and Microsoft Graph docs. Where the guide and a block here disagree on your version, the guide wins.

## The map

```text
 ┌─ your tenant (Bicep, one deployment at subscription scope) ─────────────────────────┐
 │  1. resource providers  2. custom role + app registration  3. three VNets:          │
 │     Microsoft.Nutanix      nc2-custom-role → service         cluster / prism central │
 │     Microsoft.Network      principal (Entra)                 / flow gateway, each   │
 │                                                              with a NAT gateway,    │
 │                                                              peered in a mesh,      │
 │                                                              Route Server in a hub  │
 └───────────────────────────────────────┬─────────────────────────────────────────────┘
                                         │ application id · directory id · secret · subscription id
                                         ▼
 ┌─ NC2 v2 API (cloud.nutanix.com/api/v2), five-minute JWT from a My Nutanix key ───────┐
 │  4. POST /organizations  5. POST /organizations/{id}/cloud-accounts/azure             │
 │  6. POST /clusters/azure  (cluster + Prism Central + Flow Gateways, one task)         │
 └───────────────────────────────────────┬─────────────────────────────────────────────┘
                                         │ ~45 min, poll /tasks/{id}
                                         ▼
 ┌─ Azure · region ─────────────────────────────────────────────────────────────────────┐
 │  cluster VNet ── bare-metal nodes (delegated subnet) ── AOS cluster                   │
 │  prism central VNet ── PC VM(s) (delegated subnet)  ◀── you talk to this, :9440       │
 │  flow gateway VNet ── FGW VMs (internal + external subnets) · BGP VMs ── Route Server │
 └───────────────────────────────────────┬─────────────────────────────────────────────┘
                                         │ v4 APIs
                                         ▼
 ┌─ laptop ─ tofu ─ provider nutanix 2.x ─ Prism Central ─ yesterday's files, unchanged ─┐
 └──────────────────────────────────────────────────────────────────────────────────────┘
```

Two things are different from AWS and both are in the picture. The bare-metal nodes and Prism Central sit in subnets delegated to `Microsoft.BareMetal/AzureHostedService`, and Azure allows one such subnet per VNet, so there are two VNets before you have done anything. And north-south traffic for your VMs leaves through Flow Gateway VMs that are ordinary Azure VMs in a third VNet, with BGP speakers talking to an Azure Route Server. None of that exists on AWS.

## Step 1: the parts Bicep cannot do, and what to do instead

```text
 az account set --subscription <id>
 az provider register --namespace Microsoft.Nutanix
 az provider register --namespace Microsoft.Network
 az provider show --namespace Microsoft.Nutanix --query registrationState     # Registered
```

Resource provider registration is subscription state, not a resource; the guide does it in PowerShell, `az` does the same. Two more items stay outside the template: the NC2 subscription itself (a My Nutanix workspace with the Account Admin role, a trial or a paid plan), and the app registration's client secret. Bicep can create the app and the service principal through the Microsoft Graph extension, but it will not mint a secret; that is one CLI call into Key Vault, below. Everything else is a deployment.

## Step 2: least privilege for the orchestrator: custom role and app registration

The guide's `nc2-custom-role` is the whole allow-list NC2 needs to build and run clusters in your subscription: compute, network, storage, managed identities, resource groups, tags, `Microsoft.Nutanix/*`, route tables, cost management. It is long; the file below carries the first lines and points at the guide for the rest. The app registration is what the NC2 console (or the API) logs in as.

```text
 Entra ID                              subscription
 ┌────────────────────────┐            ┌──────────────────────────────────┐
 │ app: nc2-orchestrator  │  appId ──▶ │ role assignment                  │
 │  └─ service principal  │ ◀─ id ──── │   nc2-custom-role → principal    │
 │     secret → Key Vault │            │   scope: /subscriptions/<id>     │
 └────────────────────────┘            └──────────────────────────────────┘
```

```bicep
// nc2-identity.bicep  (targetScope = 'subscription'; Graph extension enabled in bicepconfig.json)
targetScope = 'subscription'
extension microsoftGraphV1

param roleName string = 'nc2-custom-role'

// The action list is the guide's, verbatim; the full set is ~100 lines and lives in nc2-role-actions.json.
var actions = loadJsonContent('nc2-role-actions.json')

resource nc2Role 'Microsoft.Authorization/roleDefinitions@2022-04-01' = {
  name: guid(subscription().id, roleName)
  properties: {
    roleName: roleName
    description: 'Least privilege for the NC2 orchestrator (NC2 on Azure Deployment and User Guide)'
    type: 'CustomRole'
    assignableScopes: [subscription().id]
    permissions: [{ actions: actions, notActions: [] }]
  }
}

resource nc2App 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: 'nc2-orchestrator'
  displayName: 'NC2 orchestrator'
  signInAudience: 'AzureADMyOrg'
}

resource nc2Sp 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: nc2App.appId
}

resource nc2Assignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, nc2Sp.id, nc2Role.id)
  properties: {
    roleDefinitionId: nc2Role.id
    principalId: nc2Sp.id
    principalType: 'ServicePrincipal'
  }
}

output applicationId string = nc2App.appId
output directoryId string = tenant().tenantId
output subscriptionId string = subscription().subscriptionId
```

```text
 $ az deployment sub create -l westus2 -f nc2-identity.bicep
 $ az ad app credential reset --id <applicationId> --years 1 --query password -o tsv \
     | az keyvault secret set --vault-name kv-lab --name nc2-orchestrator-secret --value @- 
```

The secret goes from the CLI into Key Vault without touching the terminal history or a file. Those four values, application ID, directory ID, secret, subscription ID, are exactly what the NC2 cloud account asks for in step 5.

## Step 3: the landing zone: three VNets, delegated subnets, NAT, peering, Route Server

The sizes are the guide's CIDR table, the shape is the guide's VPN topology (a separate Flow Gateway VNet; with ExpressRoute the FGW subnets can share the Prism Central VNet). Custom DNS on every VNet is not optional: the guide says a deployment into a VNet on the Azure default resolver fails. And every NAT gateway carries the `fastpathenabled` tag the NC2 console checks for.

```text
 hub  10.10.0.0/24            cluster  10.20.0.0/24         prism central  10.30.0.0/23
 ├─ RouteServerSubnet /27     └─ mgmt /25  ◀ BareMetal      ├─ pc /26  ◀ BareMetal delegated
 └─ (vpn / er gateway)           delegated, NAT ──▶ pip     │   NAT ──▶ pip
                                                            flow gateway  10.40.0.0/23
        all four VNets peered in a full mesh                ├─ fgw-external /24  NAT ──▶ pip
        Route Server: branch-to-branch on                   ├─ fgw-internal /28
                                                            └─ bgp /28
```

```bicep
// nc2-network.bicep  (targetScope = 'resourceGroup')
param location string = resourceGroup().location
param dns array = ['8.8.8.8', '8.8.4.4']      // any resolver that answers for the public endpoints; never the Azure default

var vnets = {
  hub:  { cidr: '10.10.0.0/24', subnets: [ { name: 'RouteServerSubnet', prefix: '10.10.0.0/27' } ] }
  clstr:{ cidr: '10.20.0.0/24', subnets: [ { name: 'mgmt', prefix: '10.20.0.0/25', bareMetal: true, nat: true } ] }
  pc:   { cidr: '10.30.0.0/23', subnets: [ { name: 'pc', prefix: '10.30.0.0/26', bareMetal: true, nat: true } ] }
  fgw:  { cidr: '10.40.0.0/23', subnets: [ { name: 'fgw-external', prefix: '10.40.0.0/24', nat: true }
                                           { name: 'fgw-internal', prefix: '10.40.1.0/28' }
                                           { name: 'bgp',          prefix: '10.40.1.16/28' } ] }
}

// One NAT gateway per VNet that needs egress (cluster, prism central, flow gateway), each with its own public IP.
resource natPip 'Microsoft.Network/publicIPAddresses@2024-05-01' = [for n in ['clstr', 'pc', 'fgw']: {
  name: 'pip-nat-${n}'
  location: location
  sku: { name: 'Standard' }
  properties: { publicIPAllocationMethod: 'Static' }
}]

resource nat 'Microsoft.Network/natGateways@2024-05-01' = [for (n, i) in ['clstr', 'pc', 'fgw']: {
  name: 'nat-${n}'
  location: location
  sku: { name: 'Standard' }
  tags: { fastpathenabled: 'true' }                 // the NC2 console refuses a NAT gateway without it
  properties: { publicIpAddresses: [ { id: natPip[i].id } ], idleTimeoutInMinutes: 10 }
}]

resource vnet 'Microsoft.Network/virtualNetworks@2024-05-01' = [for n in items(vnets): {
  name: 'vnet-nc2-${n.key}'
  location: location
  properties: {
    addressSpace: { addressPrefixes: [ n.value.cidr ] }
    dhcpOptions: { dnsServers: dns }
    subnets: [for s in n.value.subnets: {
      name: s.name
      properties: union(
        { addressPrefix: s.prefix },
        contains(s, 'bareMetal') ? { delegations: [ { name: 'nc2', properties: { serviceName: 'Microsoft.BareMetal/AzureHostedService' } } ] } : {},
        contains(s, 'nat') ? { natGateway: { id: resourceId('Microsoft.Network/natGateways', 'nat-${n.key}') } } : {}
      )
    }]
  }
  dependsOn: [ nat ]
}]

// Full mesh: every VNet peered with every other, both directions, forwarded traffic allowed.
var names = [for n in items(vnets): n.key]
resource peer 'Microsoft.Network/virtualNetworks/virtualNetworkPeerings@2024-05-01' = [for p in flatten(map(names, a => map(filter(names, b => b != a), b => { a: a, b: b }))): {
  name: '${p.a}-to-${p.b}'
  parent: vnet[indexOf(names, p.a)]
  properties: {
    remoteVirtualNetwork: { id: vnet[indexOf(names, p.b)].id }
    allowVirtualNetworkAccess: true
    allowForwardedTraffic: true
    allowGatewayTransit: p.a == 'hub'
    useRemoteGateways: false
  }
}]

// Azure Route Server in the hub: the BGP speakers NC2 deploys peer with it. Branch-to-branch on, so overlay routes propagate.
resource rsPip 'Microsoft.Network/publicIPAddresses@2024-05-01' = {
  name: 'pip-rs-hub'
  location: location
  sku: { name: 'Standard' }
  properties: { publicIPAllocationMethod: 'Static' }
}

resource routeServer 'Microsoft.Network/virtualHubs@2024-05-01' = {
  name: 'rs-hub'
  location: location
  properties: { sku: 'Standard', allowBranchToBranchTraffic: true }
}

resource rsIp 'Microsoft.Network/virtualHubs/ipConfigurations@2024-05-01' = {
  name: 'ipconfig1'
  parent: routeServer
  properties: {
    subnet: { id: resourceId('Microsoft.Network/virtualNetworks/subnets', 'vnet-nc2-hub', 'RouteServerSubnet') }
    publicIPAddress: { id: rsPip.id }
  }
  dependsOn: [ vnet ]
}

output resourceGroup string = resourceGroup().name
output clusterVnet string = 'vnet-nc2-clstr'
output pcVnet string = 'vnet-nc2-pc'
output fgwVnet string = 'vnet-nc2-fgw'
```

```text
 $ az group create -n rg-nc2-lab -l westus2
 $ az deployment group create -g rg-nc2-lab -f nc2-network.bicep
   ... "provisioningState": "Succeeded"
```

Two things to know before the deploy. The peering loop is the part that times out on Azure's side more than any other; a second `az deployment group create` is idempotent and finishes what the first started. And the Route Server's soft limit is eight BGP sessions; each scale-out Flow Gateway uses two, so four FGWs is the ceiling on one Route Server.

## Step 4: a five-minute token for the NC2 API

The NC2 v2 API authenticates with a JWT you sign yourself from a My Nutanix API key (scope NC2, role Admin to create clusters). The guide's Python is the reference; this is the same thing in twelve lines.

```python
# nc2_token.py: HS512 JWT, five-minute expiry, from a My Nutanix API key (kept in the environment)
import base64, datetime, hashlib, hmac, os, uuid, jwt
key, kid = os.environ["NC2_API_KEY"], os.environ["NC2_KEY_ID"]
sig = base64.b64encode(hmac.new(key.encode("latin-1"), kid.encode("latin-1"), hashlib.sha512).digest())
now = datetime.datetime.utcnow()
print(jwt.encode({"aud": "https://apikeys.nutanix.com", "iat": now, "exp": now + datetime.timedelta(seconds=300),
                  "iss": str(uuid.uuid4()), "metadata": {"reason": "nc2 azure as code"}, "context": {}},
                 sig, algorithm="HS512", headers={"kid": kid}))
```

```text
 $ export NC2_TOKEN=$(python3 nc2_token.py)
 $ curl -s https://cloud.nutanix.com/api/v2/organizations -H "Authorization: Bearer $NC2_TOKEN"
   {"data":[{"id":"…","name":"Default", …}]}
```

Five minutes is Nutanix's recommendation, not a limit; a pipeline mints a new one per step.

## Step 5: the organization and the cloud account, by API

Yesterday this was the Organizations tab and the Add Cloud Account dialog. Both are one POST each. The organization is the tenancy boundary in the NC2 console (Finance runs Finance clusters); the cloud account is the four values from step 2.

```text
 POST /organizations                                   ─▶ 200  {id: ORG}
 POST /organizations/{ORG}/cloud-accounts/azure        ─▶ 200  task ─▶ poll /tasks/{id} ─▶ done
 GET  /organizations/{ORG}/cloud-accounts?cloud_provider=azure   ─▶ {id: ACCT, status: …}
 POST /cloud-accounts/{ACCT}/regions   (if not all_supported_regions)
```

```bash
# 5a. the organization
ORG=$(curl -s -X POST https://cloud.nutanix.com/api/v2/organizations \
  -H "Authorization: Bearer $NC2_TOKEN" -H "Content-Type: application/json" \
  -d '{"data":{"name":"lab-azure","url_slug":"lab_azure"}}' | jq -r .data.id)

# 5b. the Azure cloud account: the app registration from step 2, secret read from Key Vault at call time
SECRET=$(az keyvault secret show --vault-name kv-lab --name nc2-orchestrator-secret --query value -o tsv)
TASK=$(curl -s -X POST "https://cloud.nutanix.com/api/v2/organizations/$ORG/cloud-accounts/azure" \
  -H "Authorization: Bearer $NC2_TOKEN" -H "Content-Type: application/json" \
  -d "{\"data\":{\"name\":\"lab-sub\",\"application_id\":\"$APP_ID\",\"directory_id\":\"$TENANT_ID\",
       \"subscription_id\":\"$SUB_ID\",\"secret\":\"$SECRET\",\"all_supported_regions\":false,\"regions\":[\"westus2\"]}}" \
  | jq -r .data.id)
unset SECRET
```

The cloud-account call returns a task, not an account: NC2 logs in as the service principal, checks the role, and only then lists the account with a status. If the task fails, the role is the first suspect (a missing `Microsoft.Nutanix/*` action, or the assignment scoped to a resource group instead of the subscription).

## Step 6: the cluster, with Prism Central and Flow Gateways inside it

One POST, one task, roughly the time of a long lunch. The payload names the landing zone by resource group, VNet and subnet; NC2 does the rest, including the Prism Central VM and the Flow Gateway and BGP VMs. Field names are from the v2 reference's Azure sample; check them against the spec for your console version before the first run.

```text
 Create Azure cluster
 ├─ organization_id · customer_id · name · region · use_case general
 ├─ capacity        host_type AN36P (or AN64) · number_of_hosts 3 (3 to 28) · redundancy factor 2
 ├─ software        aos_version · license nci · software_tier pro
 ├─ network         mode existing · resource_group · vnet vnet-nc2-clstr · management_subnet mgmt · dns_servers
 └─ prism_central   mode new · version · vm_size small · resource_group · pc vnet/subnet
      └─ flow_gateway   vnet-nc2-fgw · external fgw-external · internal fgw-internal · number_of_vms 2 · vm_size
                        bgp { subnet bgp, asn } · azure_route_server { rs-hub, vnet-nc2-hub, RouteServerSubnet }
                        cluster_access vpn · ssh_key
```

```bash
TASK=$(curl -s -X POST https://cloud.nutanix.com/api/v2/clusters/azure \
  -H "Authorization: Bearer $NC2_TOKEN" -H "Content-Type: application/json" -d @- <<EOF | jq -r .data.id
{
  "organization_id": "$ORG", "customer_id": "$CUSTOMER", "name": "nc2-lab-az",
  "region": "westus2", "use_case": "general",
  "aos_version": "7.3", "license": "nci", "software_tier": "pro",
  "capacity": [{ "host_type": "AN36P", "number_of_hosts": 3 }],
  "redundancy": { "factor": 2 },
  "network": { "mode": "existing", "resource_group": "rg-nc2-lab", "vnet": "vnet-nc2-clstr",
               "management_subnet": "mgmt", "dns_servers": ["8.8.8.8", "8.8.4.4"] },
  "prism_central": {
    "mode": "new", "version": "pc.2026.1", "vm_size": "small", "resource_group": "rg-nc2-lab",
    "vnet": "vnet-nc2-pc", "subnet": "pc", "ntp_server_ip_list": ["time.windows.com"],
    "flow_gateway": {
      "resource_group": "rg-nc2-lab", "vnet": "vnet-nc2-fgw",
      "external_subnet": "fgw-external", "internal_subnet": "fgw-internal",
      "number_of_vms": 2, "vm_size": "Standard_D4_v5", "cluster_access": "vpn",
      "bgp": { "asn": 65200, "subnet": "bgp" },
      "azure_route_server": { "name": "rs-hub", "resource_group": "rg-nc2-lab",
                              "subscription_id": "$SUB_ID", "vnet_cidr": "10.10.0.0/24", "subnet_cidr": "10.10.0.0/27" },
      "ssh_key": "nc2-lab-key", "ssh_key_resource_group": "rg-nc2-lab"
    }
  }
}
EOF
)
# poll: the same loop as the reference, terminal states done | failed | cancelled
until [ "$(curl -s https://cloud.nutanix.com/api/v2/tasks/$TASK -H "Authorization: Bearer $(python3 nc2_token.py)" | jq -r .data.status)" != running ]; do sleep 60; done
```

When the task is done the NC2 console shows the cluster Running, and the Azure resource group shows what the API built for you: the bare-metal nodes on the delegated subnet, the Prism Central VM, two Flow Gateway VMs, two BGP VMs peered with the Route Server. Read the Prism Central address back from `GET /clusters/{id}`. From here it is yesterday's post: the same provider, the same `versions.tf`, the same VPC, subnets, route, image and VM files, pointed at this Prism Central. The overlay networking is Flow Virtual Networking on both clouds, which is the point of doing it this way.

## The whole run

```text
 $ az deployment sub   create -l westus2  -f nc2-identity.bicep         ✔  role · app · sp · assignment
 $ az deployment group create -g rg-nc2-lab -f nc2-network.bicep        ✔  4 vnets · 7 subnets · 3 nat · 12 peerings · route server
 $ python3 nc2_token.py                                                  ✔  jwt, 5 min
 $ POST /organizations                                                   ✔  lab-azure
 $ POST /organizations/{org}/cloud-accounts/azure                        ✔  task done, account ready
 $ POST /clusters/azure                                                  ✔  task done after ~45 min
 $ tofu apply    (yesterday's files, new pc_endpoint)                    ✔  8 added
 $ tofu plan                                                             No changes.
```

Three owners, three lines. Bicep owns the tenant and the landing zone. The NC2 API owns the organization, the cloud account, the cluster, Prism Central and the Flow Gateways. OpenTofu owns everything above Prism Central. Nothing in the chain is a screenshot.

## What to watch

- **One delegated subnet per VNet.** That is why the cluster and Prism Central have separate VNets. Trying to put both in one VNet fails at the NC2 console's pre-check, not at the Azure deploy.
- **Custom DNS, or the deploy fails.** The guide is explicit: a VNet on the Azure default resolver fails NC2 deployment. Any resolver that answers for `gateway-external-api.cloud.nutanix.com` and the download endpoints will do.
- **NAT gateways carry `fastpathenabled: true`.** The NC2 console checks the tag and stops without it. Deploying without NAT gateways at all is possible only with an NVA and a support ticket to disable the check.
- **Quotas before the cluster POST.** Bare-metal node quota for the host type, vCPUs for two to four Flow Gateway VMs (D4 or D32, v4 or v5) and two BGP VMs (D8s v5), three public IPs, and Route Server BGP sessions (two per FGW, soft limit eight).
- **Secrets never touch a file.** The client secret goes CLI to Key Vault; the API reads it back at call time and the shell unsets it. The My Nutanix API key lives in the environment; the JWT is worth five minutes.
- **The payload is the spec's, not this page's.** Field names in step 6 follow the v2 reference's Azure sample as of this writing; the reference is versioned, download the OpenAPI file it links and validate before the first real run.

Sources: NC2 on Azure Deployment and User Guide (portal.nutanix.com: Requirements for NC2 on Azure, Registering the Azure Resource Providers, Creating an Azure Custom Role, Creating Azure VNet and Subnet, Creating a NAT Gateway, Creating an Organization, Adding an Azure Cloud Account, Creating a Cluster, NC2 API Key Management); Nutanix Cloud Clusters API Reference v2 on nutanix.dev (organizations, cloud accounts, regions, Create Azure cluster, tasks); Microsoft Learn for Bicep, the Microsoft Graph Bicep extension, NAT Gateway, VNet peering and Route Server; and Jonas Werner's NC2 on Azure landing-zone write-up and repository, which settled the VNet count and the `fastpathenabled` tag. Where a block here disagrees with those on your version, they win.
