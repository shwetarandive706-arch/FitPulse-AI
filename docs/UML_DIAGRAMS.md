# FitPulse AI — Unified Modeling Language (UML) Diagrams & Architecture

### 1. Entity-Relationship (ER) Diagram
```mermaid
erDiagram
    USERS ||--o{ SUBSCRIPTIONS : "has"
    USERS ||--o{ CHECKINS : "logs"
    USERS ||--o{ QR_TOKENS : "generates"
    USERS ||--o{ AI_PREDICTIONS : "analyzed_by"
    PLANS ||--o{ SUBSCRIPTIONS : "defines"

    USERS {
        int id PK
        string role "admin | member"
        string name
        string email UK
        string phone
        string username UK
        string password_hash
        int age
        string gender
        float height_cm
        float weight_kg
        string fitness_goal
        string dietary_pref
        int has_trainer
        datetime created_at
    }

    PLANS {
        int id PK
        string name UK
        string tier
        int duration_days
        float price
        string description
        string features_json
        int is_active
    }

    SUBSCRIPTIONS {
        int id PK
        int member_id FK
        int plan_id FK
        date start_date
        date end_date
        string status "active | expired | cancelled"
        int auto_renew
        float total_paid
        string payment_status "paid | due"
        string payment_method
        datetime created_at
    }

    CHECKINS {
        int id PK
        int member_id FK
        datetime checkin_time
        datetime checkout_time
        string method "qr_code | manual"
        int duration_mins
        string notes
    }

    QR_TOKENS {
        int id PK
        string token UK
        int member_id FK
        datetime created_at
        datetime expires_at
        int is_used
    }

    AI_PREDICTIONS {
        int id PK
        int member_id FK
        datetime predicted_at
        float churn_prob
        string risk_level "Low | Medium | High"
        string factors_json
        string recommended_action
    }
```

---

### 2. Use Case Diagram
```mermaid
flowchart LR
    subgraph System ["FitPulse AI Gym System"]
        UC1(["Login & Authentication"])
        UC2(["View Dashboard & KPIs"])
        UC3(["Manage Members & Plans"])
        UC4(["Renew / Assign Subscription"])
        UC5(["Scan Dynamic QR at Turnstile"])
        UC6(["Run AI Member Churn Scan"])
        UC7(["Generate AI Workout & Diet Plan"])
        UC8(["Export Member & Attendance CSV"])
    end

    Admin(("Gym Director / Admin"))
    Member(("Gym Member"))

    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC8

    Member --> UC1
    Member --> UC5
    Member --> UC7
```

---

### 3. Sequence Diagram (Turnstile Dynamic QR Check-in)
```mermaid
sequenceDiagram
    autonumber
    actor Member as Gym Member / App
    participant Server as Flask Application
    participant TokenEngine as QR Token Engine
    participant DB as SQLite Database

    Member->>Server: Request Dynamic Access Pass (member_id)
    Server->>TokenEngine: Generate SHA-256 Token (5 min validity)
    TokenEngine->>DB: INSERT into qr_tokens (token, expires_at, is_used=0)
    Server-->>Member: Render Dynamic QR Code with countdown

    Member->>Server: Present QR Code to Turnstile Scanner
    Server->>DB: SELECT * FROM qr_tokens WHERE token = ?
    alt Token Expired or is_used == 1
        Server-->>Member: Access Denied (Invalid or Expired Token)
    else Token Valid
        Server->>DB: Check Member Active Subscription
        alt Subscription Expired
            Server-->>Member: Access Denied (Subscription Expired)
        else Subscription Active
            Server->>DB: UPDATE qr_tokens SET is_used = 1
            Server->>DB: INSERT into checkins (member_id, timestamp)
            Server-->>Member: Gate Opens (Welcome to FitPulse Gym)
        end
    end
```

---

### 4. Activity Diagram (AI Member Churn Prediction)
```mermaid
flowchart TD
    Start([Admin Requests Churn Scan]) --> Fetch[Query Active & Expired Members]
    Fetch --> Loop{For Each Member}
    Loop --> Ext[Extract Behavioral Features: Recency, Drop Ratio, Visits/Wk, Delays]
    Ext --> Scale[Apply StandardScaler]
    Scale --> ML[RandomForestClassifier.predict_proba]
    ML --> Score[Calculate Churn Probability %]
    Score --> Decision{Risk Threshold}
    Decision -- ">= 70%" --> High[Assign High Risk & Critical Retention Discount]
    Decision -- "35% - 69%" --> Med[Assign Medium Risk & Motivational Nudge]
    Decision -- "< 35%" --> Low[Assign Low Risk & Good Standing]
    High --> Log[Save Prediction in ai_predictions Table]
    Med --> Log
    Low --> Log
    Log --> Next{More Members?}
    Next -- Yes --> Loop
    Next -- No --> Render[Display Churn Analytics Dashboard]
    Render --> End([End])
```

---

### 5. Component Diagram
```mermaid
flowchart TB
    UI[Frontend Single Page App: HTML5 / CSS3 / Vanilla JS]
    API[Flask REST API Gateway: app.py]
    Auth[Authentication & Session Module: models.py]
    ML_P[AI Churn Predictor: churn_predictor.py]
    ML_R[AI Workout & Diet Recommender: recommender.py]
    ML_F[Footfall Forecaster: footfall_forecaster.py]
    DB_M[(SQLite Database: gym_system.db)]

    UI <-->|HTTP / JSON| API
    API --> Auth
    API --> ML_P
    API --> ML_R
    API --> ML_F
    Auth --> DB_M
    API --> DB_M
```
