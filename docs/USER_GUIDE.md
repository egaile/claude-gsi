# User Guide

## GSI Reference Architecture Generator

This guide explains how to use the GSI Reference Architecture Generator to create healthcare-specific Claude deployment architectures.

---

## Introduction

The GSI Reference Architecture Generator helps Global System Integrator (GSI) partners rapidly create deployment architectures for healthcare AI solutions. By selecting your use case, cloud platform, and requirements, you can generate:

- Architecture diagrams with data flows
- HIPAA compliance checklists
- Cloud-specific deployment guides
- Sample integration code

**Time saved**: Generate proposal-ready architectures in minutes instead of days.

---

## Getting Started

1. Open the application in your browser
2. Review the configuration form on the left
3. Select your options (detailed below)
4. Click "Generate Architecture"
5. Review the generated output in the tabbed dashboard

---

## Configuration Options

### Use Case

Select the primary healthcare use case for your deployment:

| Use Case | Description | Typical Integrations |
|----------|-------------|---------------------|
| **Clinical Documentation** | AI-assisted note generation and summarization | EHR systems (Epic, Cerner), dictation services |
| **Prior Authorization** | Streamline payer-provider authorization workflows | Payer portals, clearinghouses, X12 EDI |
| **Medical Coding** | ICD-10 and CPT code suggestion and validation | Coding workbenches, CDI platforms |
| **Patient Communication** | Secure messaging, appointment prep, follow-up | Patient portals, scheduling systems |

### Cloud Platform

Choose your deployment target:

| Platform | Description | Key Services |
|----------|-------------|--------------|
| **AWS Bedrock** | Amazon's managed AI service with Claude models | API Gateway, Lambda, HealthLake, Comprehend Medical |
| **GCP Vertex AI** | Google Cloud's AI platform with Claude | Cloud Run, Healthcare API, Pub/Sub |

### Integration Pattern

Select how your application will interact with Claude:

| Pattern | Best For | Characteristics |
|---------|----------|-----------------|
| **API Gateway** | Real-time user interactions | Synchronous, low latency, request/response |
| **Event-Driven** | Background processing, workflows | Asynchronous, message queues, decoupled |
| **Batch Processing** | Large document volumes, scheduled jobs | High throughput, bulk operations |

### Data Classification

Specify the sensitivity level of data being processed:

| Classification | Description | Security Requirements |
|----------------|-------------|----------------------|
| **PHI** | Protected Health Information | Full HIPAA compliance, encryption, audit logging, BAA required |
| **PII** | Personally Identifiable Information | Privacy controls, access restrictions |
| **De-identified** | Data with identifiers removed (Safe Harbor) | Reduced compliance burden |
| **Public** | Non-sensitive, publicly available | Standard security practices |

### Scale Tier

Indicate your expected deployment scale:

| Tier | User Count | Infrastructure Considerations |
|------|------------|------------------------------|
| **Pilot** | < 100 users | Minimal HA, proof of concept |
| **Production** | 100 - 10,000 users | Full redundancy, monitoring |
| **Enterprise** | 10,000+ users | Multi-region, advanced DR |

---

## Understanding the Output

After generation, you'll see a tabbed dashboard with four sections:

### Architecture Tab

- **Diagram**: Interactive Mermaid visualization showing all components and data flows
- **Components Table**: Lists each service with its purpose and whether it handles PHI
- **Data Flows**: Shows how data moves between components, with encryption status

### Compliance Tab

- **BAA Requirements**: Business Associate Agreement guidance for Anthropic and cloud services
- **Administrative Safeguards**: Workforce training, access management, incident response
- **Physical Safeguards**: Facility access, workstation security, device controls
- **Technical Safeguards**: Encryption, audit controls, access controls

Each item shows:
- The requirement
- Recommended implementation
- Priority (Required vs Recommended)

### Deployment Tab

- **Deployment Steps**: Ordered list of infrastructure setup tasks
- **IAM Policies**: Ready-to-use permission policies for your cloud platform
- **Network Configuration**: VPC, subnet, and security group specifications
- **Monitoring Setup**: Logging and alerting configuration

### Code Tab

Sample integration code in two languages:

- **Python**: Using the Anthropic SDK
- **TypeScript**: Using the Anthropic SDK

Both samples include:
- Secure API key handling
- Error handling and retries
- PHI-safe patterns

Use the language toggle to switch between samples. Click "Copy" to copy to clipboard or "Download" to save as a file.

---

## Export Options

### Export Markdown

Click "Export Markdown" in the results dashboard header to download a complete document containing all generated content in Markdown format. This is ideal for:
- Including in proposals
- Storing in documentation systems
- Sharing with stakeholders

### Copy Code

Each code block and policy has a copy button for quick clipboard access.

### Download Code

In the Code tab, use the "Download" button to save sample code as `.py` or `.ts` files.

---

## FAQ

### What is PHI?

Protected Health Information (PHI) includes any individually identifiable health information. This includes:
- Patient names and contact information
- Medical record numbers
- Dates (birth, admission, discharge, death)
- Diagnoses and treatment information
- Prescription and medication data

### Why are there two cloud platform options?

Different healthcare organizations have existing cloud relationships and compliance certifications. AWS Bedrock and GCP Vertex AI both offer HIPAA-eligible services, but with different integration patterns and service catalogs.

### Are the generated architectures production-ready?

The generated architectures represent approximately 80% of a complete solution. They should be reviewed by your security and compliance teams before production deployment. Key items to verify:
- IAM policies match your organization's least-privilege requirements
- Network configurations align with your VPC design
- Monitoring thresholds match your SLAs

### How accurate is the compliance checklist?

The HIPAA compliance items are based on the Security Rule requirements. However, your organization may have additional policies or more stringent requirements. Always consult with your compliance team.

### Can I regenerate with different options?

Yes! Click "New Architecture" to return to the configuration form and generate a new architecture with different selections.

---

## Getting Help

If you encounter issues or have questions:
- Check the [GitHub repository](https://github.com/egaile/claude-gsi) for updates
- Open an issue for bug reports or feature requests
- Contact the author via [LinkedIn](https://linkedin.com/in/edgaile)
