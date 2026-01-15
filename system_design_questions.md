# System Design Interview Questions & Answers

## Atlassian System Design Questions

### 1. Design a collaborative document editing system like Confluence

**Requirements:**
- Real-time collaborative editing
- Version control and history
- User permissions and access control
- Rich text formatting
- Comments and mentions

**High-Level Architecture:**
```
Client Apps → Load Balancer → API Gateway → Microservices
                                          ↓
Document Service ← → Collaboration Service ← → User Service
       ↓                      ↓                    ↓
   Document DB          WebSocket Server      User DB
       ↓                      ↓
   Version Store         Notification Queue
```

**Key Components:**
- **Document Service**: CRUD operations, version management
- **Collaboration Service**: Real-time sync using WebSockets/Socket.io
- **Operational Transform (OT)**: Handle concurrent edits without conflicts
- **Version Control**: Git-like system for document history
- **Permission Service**: Role-based access control
- **Search Service**: Full-text search using Elasticsearch

**Database Design:**
- **Documents**: PostgreSQL for metadata, MongoDB for content
- **Versions**: Separate table with diff storage
- **Users/Permissions**: PostgreSQL with RBAC model

**Scalability:**
- Horizontal scaling of services
- CDN for static assets
- Redis for session management
- Message queues for async operations

### 2. Design a project management tool like Jira

**Requirements:**
- Issue tracking and workflow management
- Custom fields and issue types
- Agile boards (Scrum/Kanban)
- Reporting and analytics
- Integration capabilities

**Architecture:**
```
Web/Mobile Apps → API Gateway → Microservices Layer
                                      ↓
Issue Service ← → Workflow Service ← → Project Service
     ↓                 ↓                    ↓
  Issue DB        Workflow DB          Project DB
     ↓                 ↓                    ↓
Search Index    Notification Queue    Analytics DB
```

**Core Services:**
- **Issue Service**: CRUD for issues, custom fields
- **Workflow Service**: State transitions, business rules
- **Project Service**: Project configuration, permissions
- **Board Service**: Agile board views and operations
- **Notification Service**: Email/in-app notifications
- **Analytics Service**: Reporting and metrics

**Database Schema:**
```sql
Issues: id, project_id, type, status, assignee, reporter, created_date
Projects: id, key, name, lead, workflow_scheme
Workflows: id, name, states, transitions
Custom_Fields: id, name, type, project_id
```

**Key Features:**
- Event-driven architecture for workflow transitions
- Elasticsearch for advanced search and JQL
- Redis for caching frequently accessed data
- Audit logging for compliance

### 3. Design a real-time chat system for teams

**Requirements:**
- Real-time messaging
- Group chats and channels
- File sharing
- Message history
- Online presence

**Architecture:**
```
Client Apps → Load Balancer → WebSocket Gateway
                                    ↓
Message Service ← → Presence Service ← → User Service
      ↓                   ↓                  ↓
  Message DB         Presence Cache      User DB
      ↓                   ↓
  File Storage      Push Notifications
```

**Technical Implementation:**
- **WebSocket Connections**: Socket.io or native WebSockets
- **Message Queue**: Apache Kafka for message ordering
- **Database**: Cassandra for message storage (time-series)
- **Presence**: Redis with TTL for online status
- **File Storage**: AWS S3 with CDN

**Message Flow:**
1. User sends message via WebSocket
2. Message service validates and stores
3. Kafka distributes to all channel subscribers
4. WebSocket gateway pushes to connected clients
5. Push notifications for offline users

**Scalability Considerations:**
- Consistent hashing for WebSocket server selection
- Message sharding by channel ID
- Read replicas for message history
- CDN for file attachments

### 4. Design a file sharing platform

**Requirements:**
- File upload/download
- Version control
- Sharing and permissions
- Sync across devices
- Search capabilities

**Architecture:**
```
Client Apps → CDN → API Gateway → File Service
                                      ↓
                              Metadata DB ← → Storage Service
                                      ↓           ↓
                              Search Index    Object Storage
                                      ↓           ↓
                              Sync Service    Backup Storage
```

**Core Components:**
- **File Service**: Upload/download, metadata management
- **Storage Service**: Chunked storage, deduplication
- **Sync Service**: Real-time sync across devices
- **Permission Service**: Access control and sharing
- **Search Service**: Content indexing and search

**Storage Strategy:**
- **Chunked Upload**: Large files split into chunks
- **Deduplication**: Hash-based duplicate detection
- **Versioning**: Copy-on-write for file versions
- **Compression**: Automatic compression for text files

### 5. Design a notification system

**Requirements:**
- Multiple channels (email, push, in-app)
- User preferences
- Rate limiting
- Delivery tracking
- Template management

**Architecture:**
```
Event Sources → Message Queue → Notification Service
                                       ↓
Template Service ← → Preference Service ← → Delivery Service
       ↓                    ↓                      ↓
  Template DB         Preference DB          Delivery Logs
                                                   ↓
                                            External APIs
                                         (Email, Push, SMS)
```

**Implementation:**
- **Event Processing**: Kafka for event ingestion
- **Template Engine**: Mustache/Handlebars for dynamic content
- **Rate Limiting**: Redis-based sliding window
- **Delivery Tracking**: Status updates and analytics
- **Retry Logic**: Exponential backoff for failed deliveries

## PayPal System Design Questions

### 1. Design a payment processing system

**Requirements:**
- Process millions of transactions per second
- Support multiple payment methods
- Fraud detection and prevention
- Compliance with financial regulations
- Global availability

**Architecture:**
```
Client Apps → API Gateway → Payment Service
                                 ↓
Risk Engine ← → Transaction Service ← → Account Service
     ↓                 ↓                      ↓
Fraud DB        Transaction DB           Account DB
     ↓                 ↓                      ↓
ML Models       Settlement Service      Ledger Service
```

**Core Services:**
- **Payment Service**: Payment method validation, tokenization
- **Transaction Service**: Transaction processing and state management
- **Risk Engine**: Real-time fraud detection using ML
- **Settlement Service**: Bank reconciliation and clearing
- **Ledger Service**: Double-entry bookkeeping

**Transaction Flow:**
1. Payment request validation
2. Risk assessment and fraud check
3. Payment method authorization
4. Transaction recording in ledger
5. Settlement with financial institutions
6. Notification to merchant and customer

**Security & Compliance:**
- PCI DSS compliance for card data
- Tokenization for sensitive data
- End-to-end encryption
- Audit trails for regulatory compliance

### 2. Design a fraud detection system

**Requirements:**
- Real-time fraud scoring
- Machine learning models
- Rule-based detection
- Low false positive rate
- Scalable to millions of transactions

**Architecture:**
```
Transaction Stream → Feature Engineering → ML Pipeline
                                              ↓
Rule Engine ← → Fraud Scoring Service ← → Model Service
     ↓                    ↓                     ↓
Rules DB           Decision Engine        Model Store
     ↓                    ↓                     ↓
Alert Service      Transaction DB        Training Pipeline
```

**ML Pipeline:**
- **Feature Engineering**: Real-time feature extraction
- **Model Types**: Random Forest, Neural Networks, Gradient Boosting
- **Ensemble Methods**: Combine multiple model predictions
- **Online Learning**: Continuous model updates

**Fraud Indicators:**
- Velocity checks (transaction frequency)
- Geolocation anomalies
- Device fingerprinting
- Behavioral patterns
- Network analysis

**Decision Engine:**
- Risk scoring (0-1000 scale)
- Threshold-based actions (approve/decline/review)
- A/B testing for model performance
- Feedback loop for model improvement

### 3. Design a digital wallet

**Requirements:**
- Store multiple payment methods
- P2P money transfers
- Transaction history
- Security and authentication
- Integration with merchants

**Architecture:**
```
Mobile/Web Apps → API Gateway → Wallet Service
                                     ↓
Payment Service ← → Balance Service ← → User Service
      ↓                   ↓                ↓
Payment Methods      Account Ledger    User Profiles
      ↓                   ↓                ↓
Bank APIs          Transaction History  KYC Service
```

**Key Features:**
- **Multi-factor Authentication**: Biometric, PIN, SMS
- **Tokenization**: Secure storage of payment methods
- **Real-time Balance**: Instant balance updates
- **Transaction Limits**: Daily/monthly spending limits
- **Merchant Integration**: QR codes, NFC payments

**Security Measures:**
- Hardware Security Module (HSM) for key management
- End-to-end encryption for sensitive data
- Fraud monitoring for unusual activities
- Compliance with financial regulations

### 4. Design a money transfer system

**Requirements:**
- Domestic and international transfers
- Multiple currencies
- Compliance with regulations
- Real-time processing
- Fee calculation

**Architecture:**
```
Client Apps → API Gateway → Transfer Service
                                 ↓
FX Service ← → Compliance Service ← → Settlement Service
    ↓                ↓                      ↓
Rate DB        Regulatory DB           Banking APIs
    ↓                ↓                      ↓
Fee Engine     AML/KYC Service        Nostro Accounts
```

**Transfer Flow:**
1. Transfer request validation
2. KYC/AML compliance checks
3. FX rate calculation (if cross-currency)
4. Fee calculation and deduction
5. Funds transfer to recipient
6. Settlement with correspondent banks

**Compliance Features:**
- AML (Anti-Money Laundering) screening
- KYC (Know Your Customer) verification
- Sanctions list checking
- Regulatory reporting
- Transaction monitoring

### 5. Design a merchant payment gateway

**Requirements:**
- Accept multiple payment methods
- PCI compliance
- Real-time authorization
- Webhook notifications
- Analytics and reporting

**Architecture:**
```
Merchant APIs → Gateway Service → Payment Processor
                      ↓
Webhook Service ← → Transaction Service ← → Merchant Service
       ↓                    ↓                     ↓
Queue System        Transaction DB          Merchant DB
       ↓                    ↓                     ↓
Retry Logic         Analytics DB           Settlement Reports
```

**Payment Flow:**
1. Merchant initiates payment request
2. Gateway validates and routes to processor
3. Real-time authorization from card networks
4. Transaction result stored and returned
5. Webhook notification to merchant
6. Settlement and reconciliation

**Key Features:**
- **Tokenization**: Secure card data storage
- **3D Secure**: Additional authentication layer
- **Retry Logic**: Handle temporary failures
- **Rate Limiting**: Prevent abuse
- **Analytics**: Transaction insights and reporting

## Mastercard System Design Questions

### 1. Design a credit card transaction system

**Requirements:**
- Process 65,000+ transactions per second globally
- Sub-second authorization response
- 99.999% availability
- Global network connectivity
- Fraud prevention

**Architecture:**
```
ATM/POS → Acquirer → Mastercard Network → Issuer
                           ↓
Authorization Service ← → Fraud Detection ← → Settlement Service
         ↓                      ↓                    ↓
    Auth Rules DB         Fraud Models        Settlement DB
         ↓                      ↓                    ↓
    Routing Service      Risk Scoring         Clearing House
```

**Transaction Flow (ISO 8583):**
1. **Authorization Request**: Merchant → Acquirer → Mastercard → Issuer
2. **Fraud Check**: Real-time risk assessment
3. **Authorization**: Issuer approves/declines
4. **Response**: Decision routed back to merchant
5. **Clearing**: Batch processing of approved transactions
6. **Settlement**: Actual money movement between banks

**Technical Implementation:**
- **Message Format**: ISO 8583 standard
- **Network Protocol**: TCP/IP with custom protocols
- **Database**: Distributed across multiple data centers
- **Caching**: Redis for frequently accessed data
- **Load Balancing**: Geographic routing for low latency

### 2. Design a real-time fraud detection system

**Requirements:**
- Analyze transactions in <100ms
- Machine learning models
- Global rule engine
- Low false positive rate (<1%)
- Handle 65,000+ TPS

**Architecture:**
```
Transaction Stream → Feature Store → ML Inference Engine
                                           ↓
Rule Engine ← → Fraud Scoring ← → Model Management
     ↓              ↓                    ↓
Rules DB      Decision Service      Model Registry
     ↓              ↓                    ↓
Alert System   Transaction DB       Training Pipeline
```

**ML Models:**
- **Gradient Boosting**: Transaction patterns
- **Neural Networks**: Deep learning for complex patterns
- **Isolation Forest**: Anomaly detection
- **Graph Neural Networks**: Network analysis

**Real-time Features:**
- Transaction velocity (frequency patterns)
- Merchant category analysis
- Geolocation verification
- Device fingerprinting
- Historical behavior patterns

**Decision Engine:**
- Risk score calculation (0-999)
- Dynamic thresholds based on risk appetite
- Real-time model updates
- A/B testing framework

### 3. Design a global payment network

**Requirements:**
- Connect 25,000+ financial institutions
- Support 210+ countries and territories
- Multiple currencies and payment types
- 24/7 global operations
- Regulatory compliance per region

**Architecture:**
```
Regional Data Centers → Global Network Backbone
                              ↓
Message Routing ← → Currency Conversion ← → Compliance Engine
       ↓                     ↓                      ↓
Routing Tables         FX Rate Service        Regulatory DB
       ↓                     ↓                      ↓
Load Balancer         Settlement Service     Audit Logging
```

**Network Design:**
- **Multi-region Deployment**: Americas, Europe, Asia-Pacific
- **Message Routing**: Intelligent routing based on BIN ranges
- **Protocol Support**: ISO 8583, ISO 20022
- **Redundancy**: Multiple network paths and failover
- **Latency Optimization**: Edge locations for faster processing

**Global Considerations:**
- **Regulatory Compliance**: Local data residency requirements
- **Currency Support**: Real-time FX rates and conversion
- **Time Zone Handling**: 24/7 operations across time zones
- **Language Support**: Multi-language error messages
- **Local Partnerships**: Regional acquiring relationships

### 4. Design a loyalty rewards system

**Requirements:**
- Points earning and redemption
- Multiple reward categories
- Partner integrations
- Real-time balance updates
- Fraud prevention for rewards

**Architecture:**
```
Transaction Events → Points Engine → Rewards Catalog
                          ↓               ↓
Balance Service ← → Redemption Service ← → Partner APIs
       ↓                    ↓                  ↓
Points Ledger        Redemption History   Partner DB
       ↓                    ↓                  ↓
Audit Trail         Notification Service  Settlement
```

**Points System:**
- **Earning Rules**: Configurable point multipliers
- **Expiration Logic**: Time-based point expiry
- **Tier Management**: Status levels (Silver, Gold, Platinum)
- **Bonus Campaigns**: Promotional point offers
- **Real-time Processing**: Instant point crediting

**Redemption Options:**
- **Cash Back**: Direct account credit
- **Travel Rewards**: Airline/hotel partnerships
- **Merchandise**: Online catalog integration
- **Gift Cards**: Digital and physical cards
- **Experiences**: Event tickets and exclusive offers

### 5. Design a merchant acquiring platform

**Requirements:**
- Onboard merchants globally
- Risk assessment and underwriting
- Transaction processing
- Settlement and reporting
- Compliance management

**Architecture:**
```
Merchant Portal → Onboarding Service → Risk Assessment
                        ↓                    ↓
KYC Service ← → Underwriting Engine ← → Pricing Service
     ↓                 ↓                      ↓
Identity DB      Risk Models DB         Pricing Rules
     ↓                 ↓                      ↓
Compliance      Transaction Processing   Settlement Service
```

**Onboarding Process:**
1. **Application Submission**: Merchant details and documentation
2. **KYC Verification**: Identity and business verification
3. **Risk Assessment**: Credit checks and business analysis
4. **Underwriting Decision**: Approval/decline with terms
5. **Account Setup**: Terminal configuration and testing
6. **Go-Live**: Production transaction processing

**Risk Management:**
- **Credit Scoring**: Financial stability assessment
- **Industry Risk**: MCC-based risk categorization
- **Transaction Monitoring**: Unusual pattern detection
- **Reserve Management**: Risk-based fund holds
- **Chargeback Management**: Dispute handling and prevention

## Additional Questions Found Online

### Atlassian Additional Questions
- **Design a code review system like Crucible**
- **Design a service desk system**
- **Design a knowledge base search system**
- **Design a team calendar and resource planning system**
- **Design a CI/CD pipeline management system**

### PayPal Additional Questions  
- **Design a cryptocurrency exchange**
- **Design a buy-now-pay-later system**
- **Design a merchant onboarding system**
- **Design a cross-border remittance system**
- **Design a payment analytics platform**

### Mastercard Additional Questions
- **Design a contactless payment system**
- **Design a tokenization service**
- **Design a chargeback management system**
- **Design a merchant analytics platform**
- **Design a regulatory reporting system**

## Common System Design Patterns

### Scalability Patterns
- **Horizontal Scaling**: Add more servers
- **Vertical Scaling**: Increase server capacity
- **Load Balancing**: Distribute traffic evenly
- **Caching**: Redis/Memcached for fast access
- **CDN**: Geographic content distribution

### Reliability Patterns
- **Circuit Breaker**: Prevent cascade failures
- **Retry Logic**: Handle transient failures
- **Bulkhead**: Isolate critical resources
- **Timeout**: Prevent hanging requests
- **Health Checks**: Monitor service status

### Security Patterns
- **Authentication**: Multi-factor verification
- **Authorization**: Role-based access control
- **Encryption**: Data protection in transit/rest
- **Rate Limiting**: Prevent abuse and DoS
- **Input Validation**: Sanitize user inputs

### Data Patterns
- **CQRS**: Separate read/write operations
- **Event Sourcing**: Store events, not state
- **Saga Pattern**: Distributed transactions
- **Database Sharding**: Horizontal data partitioning
- **Read Replicas**: Scale read operations
