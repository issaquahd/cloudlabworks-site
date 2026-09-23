# LinkedIn: NC2 on Google Cloud, day one, pure v4 API (draft, not yet published)

Site post (canonical, link goes at the top and the bottom of the article and in the feed post):
https://cloudlabworks.dev/nutanix/nc2-gcp-day-one-pure-v4-api

Two pieces, like the AWS, Azure and GCP posts: an **article** (LinkedIn, Write article) and a **post**
that links it. The article carries the map as an image (`linkedin/src` panel to render from the ASCII
block in the site post); code stays on the site.

---

## Post (feed)

Yesterday's post built NC2 on Google Cloud with Pulumi and one call to the NC2 console API. Today's is the half that matters more: what happens after Prism Central answers.

Seven calls. One API, one version. Cluster lookup, overlay VPC, subnet, image, VM, power on, floating IP. Every one of them is the Prism Central v4 API at v4.1, every one of them is curl, and not one of them mentions Google. Run the same seven against NC2 on AWS, NC2 on Azure, or the cluster in the rack and nothing changes.

Three things the specification says that I would not have guessed:

Every POST needs a request ID you generate, so a retry is idempotent instead of a second VPC.

Every action on an existing resource needs the ETag you last read, or the answer is 428 Precondition Required. Two automations cannot both change a VM they read at different times.

Pin the lowest v4 minor whose floor your oldest Prism Central clears. For these seven calls that is v4.1, minimum pc.2024.3, which every NC2 cluster on Google Cloud meets.

Full walk, every request body, every source, on the site: https://cloudlabworks.dev/nutanix/nc2-gcp-day-one-pure-v4-api

#Nutanix #NC2 #GoogleCloud #HybridCloud #API #InfrastructureAsCode #CloudLabWorks

---

## Article

Full post, every request body, every source: https://cloudlabworks.dev/nutanix/nc2-gcp-day-one-pure-v4-api

[Body: the site post verbatim from "The previous post built the Google Cloud landing zone..." through "What is sourced from where", with the map ASCII block inserted as an image after the first paragraph and the seven code blocks kept as code where LinkedIn allows, otherwise as images.]

Read the rest, and the three posts before it, at https://cloudlabworks.dev/nutanix
