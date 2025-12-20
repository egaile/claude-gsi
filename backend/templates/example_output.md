# Example Architecture Output

This file contains example outputs to guide Claude in generating properly structured architecture responses.

## Example: Clinical Documentation on AWS Bedrock

### Input Configuration
```json
{
  "useCase": "clinical-documentation",
  "cloudPlatform": "aws-bedrock",
  "integrationPattern": "api-gateway",
  "dataClassification": "phi",
  "scaleTier": "production"
}
```

### Expected Output Structure
```json
{
  "architecture": {
    "mermaidDiagram": "flowchart TD\n    subgraph Client[\"Healthcare Application\"]\n        ehr[EHR System\\nEpic/Cerner]\n        app[Clinical App]\n    end\n    \n    subgraph AWS[\"AWS Cloud - HIPAA Eligible\"]\n        subgraph Public[\"Public Subnet\"]\n            apigw[API Gateway\\n+ WAF]\n        end\n        \n        subgraph Private[\"Private Subnet\"]\n            lambda[Lambda\\nDocument Processor]\n            comprehend[Comprehend Medical\\nPHI Detection]\n        end\n        \n        subgraph AI[\"AI Services\"]\n            bedrock[Amazon Bedrock\\nClaude Sonnet]\n        end\n        \n        subgraph Data[\"Data Layer\"]\n            healthlake[(HealthLake\\nFHIR Store)]\n            s3[(S3\\nDocument Archive)]\n        end\n        \n        subgraph Security[\"Security Services\"]\n            secrets[Secrets Manager]\n            kms[KMS]\n            cloudwatch[CloudWatch\\nAudit Logs]\n        end\n    end\n    \n    ehr -->|FHIR R4| apigw\n    app -->|REST API| apigw\n    apigw -->|Authorize| lambda\n    lambda -->|Detect PHI| comprehend\n    lambda -->|Generate| bedrock\n    lambda -->|Store| healthlake\n    lambda -->|Archive| s3\n    lambda -.->|Get Keys| secrets\n    s3 -.->|Encrypt| kms\n    lambda -.->|Log| cloudwatch\n    \n    style bedrock fill:#8B5CF6,color:#fff\n    style healthlake fill:#f59e0b,color:#fff\n    style comprehend fill:#10b981,color:#fff",
    "components": [
      {
        "name": "API Gateway",
        "service": "Amazon API Gateway",
        "purpose": "REST API entry point with WAF protection, authentication, and rate limiting",
        "phiTouchpoint": true
      },
      {
        "name": "Lambda Processor",
        "service": "AWS Lambda",
        "purpose": "Orchestrates document processing workflow, handles PHI detection and Claude invocation",
        "phiTouchpoint": true
      },
      {
        "name": "Comprehend Medical",
        "service": "Amazon Comprehend Medical",
        "purpose": "Detects and extracts PHI from clinical text for logging and compliance",
        "phiTouchpoint": true
      },
      {
        "name": "Bedrock Claude",
        "service": "Amazon Bedrock (Claude)",
        "purpose": "Generates clinical documentation summaries and structured notes",
        "phiTouchpoint": true
      },
      {
        "name": "HealthLake",
        "service": "Amazon HealthLake",
        "purpose": "FHIR-compliant storage for patient data and generated documentation",
        "phiTouchpoint": true
      },
      {
        "name": "S3 Archive",
        "service": "Amazon S3",
        "purpose": "Long-term storage for original documents with encryption",
        "phiTouchpoint": true
      },
      {
        "name": "CloudWatch",
        "service": "Amazon CloudWatch",
        "purpose": "Centralized logging and monitoring for compliance audit trails",
        "phiTouchpoint": false
      }
    ],
    "dataFlows": [
      {
        "from": "EHR System",
        "to": "API Gateway",
        "data": "Clinical notes, patient context (FHIR DocumentReference)",
        "encrypted": true
      },
      {
        "from": "Lambda",
        "to": "Bedrock",
        "data": "Clinical text for summarization (may contain PHI)",
        "encrypted": true
      },
      {
        "from": "Lambda",
        "to": "HealthLake",
        "data": "Generated documentation (FHIR DocumentReference)",
        "encrypted": true
      }
    ]
  },
  "compliance": {
    "checklist": [
      {
        "category": "administrative",
        "requirement": "Designated Security Official",
        "implementation": "Assign HIPAA Security Officer responsible for this deployment",
        "priority": "required"
      },
      {
        "category": "administrative",
        "requirement": "Risk Analysis",
        "implementation": "Document risks specific to AI-assisted documentation, including prompt injection and hallucination risks",
        "priority": "required"
      },
      {
        "category": "administrative",
        "requirement": "Workforce Training",
        "implementation": "Train clinical staff on proper use of AI documentation tools and review requirements",
        "priority": "required"
      },
      {
        "category": "administrative",
        "requirement": "Business Associate Agreement",
        "implementation": "Execute BAAs with AWS (via AWS Artifact) and ensure Bedrock is covered",
        "priority": "required"
      },
      {
        "category": "technical",
        "requirement": "Unique User Identification",
        "implementation": "Implement user authentication via API Gateway with unique identifiers passed to CloudWatch logs",
        "priority": "required"
      },
      {
        "category": "technical",
        "requirement": "Audit Controls",
        "implementation": "Enable CloudTrail for all API calls, CloudWatch Logs for Lambda, and S3 access logging",
        "priority": "required"
      },
      {
        "category": "technical",
        "requirement": "Encryption - At Rest",
        "implementation": "Enable SSE-KMS for S3, DynamoDB, and HealthLake with customer-managed keys",
        "priority": "required"
      },
      {
        "category": "technical",
        "requirement": "Encryption - In Transit",
        "implementation": "Enforce TLS 1.2+ on API Gateway, use VPC endpoints for internal AWS traffic",
        "priority": "required"
      },
      {
        "category": "technical",
        "requirement": "Access Controls",
        "implementation": "Implement least-privilege IAM policies, use Secrets Manager for API keys",
        "priority": "required"
      },
      {
        "category": "physical",
        "requirement": "Data Center Security",
        "implementation": "AWS manages physical security; verify HIPAA eligibility of all services used",
        "priority": "required"
      }
    ],
    "baaRequirements": "AWS Business Associate Addendum (BAA) must be executed via AWS Artifact before processing PHI. Verify that all services used (API Gateway, Lambda, Bedrock, HealthLake, S3, CloudWatch, Secrets Manager, KMS) are listed as HIPAA-eligible services in the AWS BAA. Note: As of deployment, confirm Bedrock's HIPAA eligibility status for the specific Claude model version."
  },
  "deployment": {
    "steps": [
      "1. **Prerequisites**: Execute AWS BAA via AWS Artifact, create dedicated AWS account for PHI workloads",
      "2. **Network Setup**: Create VPC with public/private subnets, configure NAT Gateway, create VPC endpoints for AWS services (Bedrock, S3, Secrets Manager)",
      "3. **Security Foundation**: Create KMS key for PHI encryption, configure Secrets Manager for API credentials, set up CloudTrail and CloudWatch Log Groups",
      "4. **IAM Configuration**: Create Lambda execution role with least-privilege permissions, create API Gateway authorizer role",
      "5. **Data Layer**: Provision HealthLake data store with encryption, create S3 bucket with versioning and encryption enabled",
      "6. **Compute Layer**: Deploy Lambda function in VPC private subnet, configure environment variables (no secrets in code)",
      "7. **API Layer**: Create API Gateway REST API, configure WAF rules, set up authentication (Cognito or custom authorizer)",
      "8. **Monitoring**: Configure CloudWatch dashboards, set up alerts for errors and unusual access patterns",
      "9. **Testing**: Perform security testing, validate audit logging, test PHI handling workflow",
      "10. **Documentation**: Document architecture decisions, create runbooks, establish incident response procedures"
    ],
    "iamPolicies": [
      "Lambda execution role: bedrock:InvokeModel, comprehend-medical:DetectEntitiesV2, healthlake:*, s3:PutObject/GetObject, secretsmanager:GetSecretValue, logs:CreateLogGroup/CreateLogStream/PutLogEvents, ec2:CreateNetworkInterface/DescribeNetworkInterfaces/DeleteNetworkInterface (for VPC)",
      "API Gateway role: lambda:InvokeFunction",
      "KMS key policy: Allow Lambda role to encrypt/decrypt, deny all other principals"
    ],
    "networkConfig": "VPC with CIDR 10.0.0.0/16, public subnets (10.0.1.0/24, 10.0.2.0/24) for NAT Gateway, private subnets (10.0.10.0/24, 10.0.11.0/24) for Lambda. VPC endpoints for: com.amazonaws.region.bedrock-runtime, com.amazonaws.region.s3, com.amazonaws.region.secretsmanager. Security groups: Lambda SG allows outbound 443 only, VPC endpoint SG allows inbound 443 from Lambda SG.",
    "monitoringSetup": "CloudWatch Log Groups: /aws/lambda/clinical-doc-processor (90 day retention), /aws/apigateway/clinical-doc-api. CloudTrail: Multi-region trail with S3 delivery and CloudWatch Logs integration. Alarms: Lambda errors > 5/minute, API Gateway 5xx > 10/minute, Unauthorized access attempts > 3/minute. Dashboard: Request volume, latency percentiles, error rates, Bedrock token usage."
  },
  "sampleCode": {
    "python": "import json\nimport boto3\nfrom botocore.config import Config\n\n# Configure Bedrock client with retry logic\nbedrock_config = Config(\n    retries={'max_attempts': 3, 'mode': 'adaptive'}\n)\nbedrock = boto3.client('bedrock-runtime', config=bedrock_config)\n\ndef invoke_claude(clinical_text: str, patient_context: dict) -> str:\n    \"\"\"\n    Invoke Claude via Bedrock for clinical documentation.\n    \n    IMPORTANT: Ensure PHI handling compliance before calling.\n    This function assumes clinical_text may contain PHI.\n    \"\"\"\n    # System prompt for clinical documentation\n    system_prompt = \"\"\"You are a clinical documentation assistant. \n    Generate a structured clinical note summary based on the provided text.\n    Follow standard medical documentation format (SOAP notes).\n    Do not add information not present in the source text.\"\"\"\n    \n    messages = [\n        {\n            \"role\": \"user\",\n            \"content\": f\"\"\"Patient Context:\n- Age: {patient_context.get('age', 'Not provided')}\n- Chief Complaint: {patient_context.get('chief_complaint', 'Not provided')}\n\nClinical Notes to Summarize:\n{clinical_text}\n\nGenerate a structured SOAP note summary.\"\"\"\n        }\n    ]\n    \n    response = bedrock.invoke_model(\n        modelId='anthropic.claude-3-sonnet-20240229-v1:0',\n        contentType='application/json',\n        accept='application/json',\n        body=json.dumps({\n            'anthropic_version': 'bedrock-2023-05-31',\n            'max_tokens': 2048,\n            'system': system_prompt,\n            'messages': messages\n        })\n    )\n    \n    response_body = json.loads(response['body'].read())\n    return response_body['content'][0]['text']\n\n\ndef lambda_handler(event, context):\n    \"\"\"\n    Lambda handler for clinical documentation requests.\n    \n    Expected event structure:\n    {\n        \"clinicalText\": \"string\",\n        \"patientContext\": {\n            \"age\": \"string\",\n            \"chief_complaint\": \"string\"\n        },\n        \"requestId\": \"string\",\n        \"userId\": \"string\"\n    }\n    \"\"\"\n    # Log request (without PHI) for audit\n    print(json.dumps({\n        'action': 'clinical_doc_request',\n        'requestId': event.get('requestId'),\n        'userId': event.get('userId'),\n        'timestamp': context.aws_request_id\n    }))\n    \n    try:\n        result = invoke_claude(\n            event['clinicalText'],\n            event.get('patientContext', {})\n        )\n        \n        return {\n            'statusCode': 200,\n            'body': json.dumps({\n                'summary': result,\n                'requestId': event.get('requestId')\n            })\n        }\n    except Exception as e:\n        # Log error without exposing PHI\n        print(json.dumps({\n            'action': 'clinical_doc_error',\n            'requestId': event.get('requestId'),\n            'error_type': type(e).__name__\n        }))\n        raise",
    "typescript": "import {\n  BedrockRuntimeClient,\n  InvokeModelCommand,\n} from '@aws-sdk/client-bedrock-runtime';\n\ninterface PatientContext {\n  age?: string;\n  chiefComplaint?: string;\n}\n\ninterface ClinicalDocRequest {\n  clinicalText: string;\n  patientContext?: PatientContext;\n  requestId: string;\n  userId: string;\n}\n\ninterface ClaudeResponse {\n  content: Array<{ text: string }>;\n}\n\nconst bedrockClient = new BedrockRuntimeClient({\n  maxAttempts: 3,\n});\n\n/**\n * Invoke Claude via Bedrock for clinical documentation.\n * \n * IMPORTANT: Ensure PHI handling compliance before calling.\n * This function assumes clinicalText may contain PHI.\n */\nasync function invokeClaude(\n  clinicalText: string,\n  patientContext: PatientContext = {}\n): Promise<string> {\n  const systemPrompt = `You are a clinical documentation assistant.\nGenerate a structured clinical note summary based on the provided text.\nFollow standard medical documentation format (SOAP notes).\nDo not add information not present in the source text.`;\n\n  const userMessage = `Patient Context:\n- Age: ${patientContext.age ?? 'Not provided'}\n- Chief Complaint: ${patientContext.chiefComplaint ?? 'Not provided'}\n\nClinical Notes to Summarize:\n${clinicalText}\n\nGenerate a structured SOAP note summary.`;\n\n  const command = new InvokeModelCommand({\n    modelId: 'anthropic.claude-3-sonnet-20240229-v1:0',\n    contentType: 'application/json',\n    accept: 'application/json',\n    body: JSON.stringify({\n      anthropic_version: 'bedrock-2023-05-31',\n      max_tokens: 2048,\n      system: systemPrompt,\n      messages: [{ role: 'user', content: userMessage }],\n    }),\n  });\n\n  const response = await bedrockClient.send(command);\n  const responseBody: ClaudeResponse = JSON.parse(\n    new TextDecoder().decode(response.body)\n  );\n\n  return responseBody.content[0].text;\n}\n\n/**\n * Lambda handler for clinical documentation requests.\n */\nexport async function handler(\n  event: ClinicalDocRequest\n): Promise<{ statusCode: number; body: string }> {\n  // Log request (without PHI) for audit\n  console.log(\n    JSON.stringify({\n      action: 'clinical_doc_request',\n      requestId: event.requestId,\n      userId: event.userId,\n      timestamp: new Date().toISOString(),\n    })\n  );\n\n  try {\n    const result = await invokeClaude(\n      event.clinicalText,\n      event.patientContext\n    );\n\n    return {\n      statusCode: 200,\n      body: JSON.stringify({\n        summary: result,\n        requestId: event.requestId,\n      }),\n    };\n  } catch (error) {\n    // Log error without exposing PHI\n    console.log(\n      JSON.stringify({\n        action: 'clinical_doc_error',\n        requestId: event.requestId,\n        errorType: error instanceof Error ? error.name : 'Unknown',\n      })\n    );\n    throw error;\n  }\n}"
  }
}
```

## Notes on Output Quality

1. **Mermaid Diagrams**: Keep them readable with 8-15 nodes maximum. Use subgraphs to group related components. Always include security and data layers.

2. **Compliance Checklists**: Be specific to the use case. Don't just list generic HIPAA requirements—explain how they apply to this specific architecture.

3. **Deployment Steps**: Make them actionable. Include the "why" not just the "what." Reference specific AWS/GCP services.

4. **Sample Code**: Must be production-quality with proper error handling, logging, and comments. Never include hardcoded secrets.
