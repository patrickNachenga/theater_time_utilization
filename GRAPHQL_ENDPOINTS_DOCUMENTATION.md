# Theatre Time Utilization Microservice

## Overview

This is a **Strawberry GraphQL** (Python) API served via **FastAPI**. All endpoints are aggregated under a single GraphQL endpoint.

- **GraphQL API URL (production):** `POST /graphql`
- **GraphQL Playground (development):** `GET /gui`
- **Schema Type:** Strawberry GraphQL (SDL-based)
- **Transport:** HTTP (standard GraphQL-over-HTTP POST)

---

## Authentication & Authorization

### JWT Authentication

Every request **must** include a valid JWT Bearer token in the `Authorization` header:

```
Authorization: Bearer <token>
```

The token is decoded and validated server-side. The payload (e.g., `user_guid`, `username`, `perm_version`, `groups`) is extracted for permission resolution.

### Permission Model

Each field is protected by **`CustomPermissionExtension`** which checks:

1. **Is the user authenticated?** (valid JWT token present)
2. **Are permissions resolved?** (fetched from Redis cache or Auth Service)
3. **Does the user have the required permission code?**
4. **Admin bypass**: Users in the `admin` group automatically pass all permission checks.

### Permission Codes (per module)

| Module                    | View Permission Code                  | Register Permission Code                  |
|---------------------------|---------------------------------------|-------------------------------------------|
| Procedure Delay Category  | `VIEW_PROCEDURE_DELAY_CATEGORIES`     | `REGISTER_PROCEDURE_DELAY_CATEGORIES`     |
| Procedure Delay Cause     | `VIEW_PROCEDURE_DELAY_CAUSES`         | `REGISTER_PROCEDURE_DELAY_CAUSES`         |
| Procedure                 | `VIEW_PROCEDURES`                     | `REGISTER_PROCEDURES`                     |
| Theatre Role              | `VIEW_THEATRE_ROLES`                  | `REGISTER_THEATRE_ROLES`                  |
| Theatre Member            | `VIEW_THEATRE_MEMBERS`                | `REGISTER_THEATRE_MEMBERS`                |
| Theatre Member Role       | `VIEW_THEATRE_MEMBER_ROLES`           | `REGISTER_THEATRE_MEMBER_ROLES`           |
| Region                    | `VIEW_REGIONS`                        | `REGISTER_REGIONS`                        |
| Internal Source           | `VIEW_INTERNAL_SOURCES`               | `REGISTER_INTERNAL_SOURCES`               |
| External Source           | `VIEW_EXTERNAL_SOURCES`               | `REGISTER_EXTERNAL_SOURCES`               |
| Theatre Unit              | `VIEW_THEATRE_UNITS`                  | `REGISTER_THEATRE_UNITS`                  |
| Death Reason              | `VIEW_DEATH_REASONS`                  | `REGISTER_DEATH_REASONS`                  |
| Theatre Time Record       | `VIEW_THEATRE_TIME_RECORDS`           | `REGISTER_THEATRE_TIME_RECORDS`           |
| Theatre Record Team Member| `VIEW_THEATRE_RECORD_TEAM_MEMBERS`    | `REGISTER_THEATRE_RECORD_TEAM_MEMBERS`    |
| Theatre Record Delay      | `VIEW_THEATRE_RECORD_DELAYS`          | `REGISTER_THEATRE_RECORD_DELAYS`          |

### Response Codes (from `ResponseCode` class)

| Code  | Constant              | Meaning                          |
|-------|-----------------------|----------------------------------|
| 8000  | SUCCESS               | Operation successful             |
| 8001  | INVALID_REQUEST       | Request validation failed        |
| 8002  | NO_RECORD_FOUND       | No matching records              |
| 8003  | UNAUTHORIZED          | Not authenticated                |
| 8004  | DUPLICATE             | Duplicate entry                  |
| 8005  | FAILURE               | General operation failure        |
| 8006  | DATA_IN_USE           | Cannot delete, data in use       |
| 8007  | BAD_REQUEST           | Malformed request                |
| 8009  | RESTRICTED_ACCESS     | No permission (forbidden)        |

---

## Shared Types

### Pagination

Every `get_*` query accepts the same `PaginationInput`:

```graphql
input PaginationInput {
  offset: Int! = 0    # Starting index (default 0)
  limit: Int! = 10    # Page size (default 10)
  search: String      # Optional search term
}
```

All paginated responses return a `*ListNode` type with:

```graphql
type *ListNode {
  items: [*Node!]!
  total_count: Int!
}
```

**Server-side search** is performed against a list of searchable fields specified per module (see each module below). The search is case-insensitive, matching partial strings anywhere in the field value (SQL `ILIKE '%search%'`).

### Common Response Envelope

All fields return a `Response<T>` envelope:

```graphql
type Response {
  status: Boolean!
  code: Int!
  message: String!
  data: T  # The actual payload (node or list node)
}
```

### Base64 Excel Input/Output (for Import/Download Template)

```graphql
input Base64ExcelInput {
  file_name: String!
  base64_data: String!       # Base64-encoded Excel file content
}

type Base64ExcelOutput {
  file_name: String!
  base64_data: String!       # Base64-encoded Excel file content
}
```

All download template queries return `Response[Base64ExcelOutput]`.  
All import from Excel mutations return `Response[*ListNode]` (the same list node returned by the corresponding `get*` query).

---

# Complete List of Endpoints

## 1. Procedure Delay Categories

### Query: `getProcedureDelayCategories`

```graphql
query GetProcedureDelayCategories($pagination: PaginationInput!) {
  getProcedureDelayCategories(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
        description
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_PROCEDURE_DELAY_CATEGORIES`  
**Searchable fields:** `name`, `code`, `description`  
**Input:**

| Variable      | Type              | Description                              |
|---------------|-------------------|------------------------------------------|
| pagination    | PaginationInput!  | offset (default 0), limit (default 10), search |

**`ProcedureDelayCategoryNode` fields returned:**

| Field       | Type     | Description                       |
|-------------|----------|-----------------------------------|
| uid         | String!  | Unique identifier (UUID)          |
| name        | String!  | Category name                     |
| code        | String?  | Short code                        |
| description | String?  | Description                       |

### Query: `downloadProcedureDelayCategoryTemplate`

```graphql
query DownloadProcedureDelayCategoryTemplate {
  downloadProcedureDelayCategoryTemplate {
    status
    code
    message
    data {
      file_name
      base64_data
    }
  }
}
```

**Required Permission:** `VIEW_PROCEDURE_DELAY_CATEGORIES`  
**Returns:** `Response[Base64ExcelOutput]` — A base64-encoded `.xlsx` file with columns: `name`, `code`, `description`.  
**Template columns:**

| Column      | Width | Example                                               |
|-------------|-------|-------------------------------------------------------|
| name        | 40    | Equipment Failure                                     |
| code        | 20    | PDC01                                                 |
| description | 50    | Delay due to equipment malfunction or unavailability  |

### Mutation: `registerProcedureDelayCategories`

```graphql
mutation RegisterProcedureDelayCategories($inputs: [ProcedureDelayCategoryInput!]!) {
  registerProcedureDelayCategories(inputs: $inputs) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
        description
      }
      totalCount
    }
  }
}
```

**Required Permission:** `REGISTER_PROCEDURE_DELAY_CATEGORIES`  
**Input variables:**

```graphql
input ProcedureDelayCategoryInput {
  uid: String        # Optional: for updates, omit for create
  name: String!      # Required
  code: String
  description: String
}
```

**Usage:** Pass a **list** of inputs. Supports **batch create/update**. If `uid` is provided, it updates the existing record. If omitted, a new record is created. Returns the full list of resulting records.

### Mutation: `importProcedureDelayCategoriesFromExcel`

```graphql
mutation ImportProcedureDelayCategoriesFromExcel($fileInput: Base64ExcelInput!) {
  importProcedureDelayCategoriesFromExcel(fileInput: $fileInput) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
        description
      }
      totalCount
    }
  }
}
```

**Required Permission:** `REGISTER_PROCEDURE_DELAY_CATEGORIES`  
**Input:** `fileInput: Base64ExcelInput!` — A base64-encoded Excel file matching the template columns (`name`, `code`, `description`).  
**Returns:** `Response[ProcedureDelayCategoryListNode]` — The same list node returned by `getProcedureDelayCategories`.

---

## 2. Procedure Delay Causes

### Query: `getProcedureDelayCauses`

```graphql
query GetProcedureDelayCauses($pagination: PaginationInput!) {
  getProcedureDelayCauses(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
        description
        procedureDelayCategoryUid
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_PROCEDURE_DELAY_CAUSES`  
**Searchable fields:** `name`, `code`, `description`

**`ProcedureDelayCauseNode` fields:**

| Field                       | Type     | Description                                |
|-----------------------------|----------|--------------------------------------------|
| uid                         | String!  | Unique identifier                          |
| name                        | String!  | Cause name                                 |
| code                        | String?  | Short code                                 |
| description                 | String?  | Description                                |
| procedureDelayCategoryUid   | String?  | FK to Procedure Delay Category             |

### Mutation: `registerProcedureDelayCauses`

```graphql
mutation RegisterProcedureDelayCauses($inputs: [ProcedureDelayCauseInput!]!) {
  registerProcedureDelayCauses(inputs: $inputs) {
    status
    code
    message
    data { ... }
  }
}
```

**Required Permission:** `REGISTER_PROCEDURE_DELAY_CAUSES`

```graphql
input ProcedureDelayCauseInput {
  uid: String
  name: String!
  code: String
  description: String
  procedureDelayCategoryUid: String   # FK to parent category
}
```

---

## 3. Procedures

### Query: `getProcedures`

```graphql
query GetProcedures($pagination: PaginationInput!) {
  getProcedures(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
        estimatedMinutes
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_PROCEDURES`  
**Searchable fields:** `name`, `code`

**`ProcedureNode` fields:**

| Field            | Type     | Description                      |
|------------------|----------|----------------------------------|
| uid              | String!  | Unique identifier                |
| name             | String!  | Procedure name                   |
| code             | String?  | Procedure code                   |
| estimatedMinutes | Int?     | Estimated duration in minutes    |

### Mutation: `registerProcedures`

```graphql
mutation RegisterProcedures($inputs: [ProcedureInput!]!) {
  registerProcedures(inputs: $inputs) { ... }
}
```

**Required Permission:** `REGISTER_PROCEDURES`

```graphql
input ProcedureInput {
  uid: String
  name: String!
  code: String
  estimatedMinutes: Int
}
```

---

## 4. Theatre Roles

### Query: `getTheatreRoles`

```graphql
query GetTheatreRoles($pagination: PaginationInput!) {
  getTheatreRoles(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        name
        description
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_THEATRE_ROLES`  
**Searchable fields:** `name`, `description`

**`TheatreRoleNode` fields:**

| Field       | Type     | Description               |
|-------------|----------|---------------------------|
| uid         | String!  | Unique identifier         |
| name        | String!  | Role name (e.g. Surgeon)  |
| description | String?  | Role description          |

### Mutation: `registerTheatreRoles`

```graphql
mutation RegisterTheatreRoles($inputs: [TheatreRoleInput!]!) {
  registerTheatreRoles(inputs: $inputs) { ... }
}
```

**Required Permission:** `REGISTER_THEATRE_ROLES`

```graphql
input TheatreRoleInput {
  uid: String
  name: String!
  description: String
}
```

---

## 5. Theatre Members

### Query: `getTheatreMembers`

```graphql
query GetTheatreMembers($pagination: PaginationInput!) {
  getTheatreMembers(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        userUid
        firstName
        middleName
        lastName
        pfNumber
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_THEATRE_MEMBERS`  
**Searchable fields:** `first_name`, `last_name`, `pf_number`

**`TheatreMemberNode` fields:**

| Field      | Type     | Description                               |
|------------|----------|-------------------------------------------|
| uid        | String!  | Unique identifier                         |
| userUid    | String?  | FK to SSO/Auth user (if linked)           |
| firstName  | String?  | First name                                |
| middleName | String?  | Middle name                               |
| lastName   | String?  | Last name                                 |
| pfNumber   | String?  | Staff pay-roll number                     |

### Mutation: `registerTheatreMembers`

```graphql
mutation RegisterTheatreMembers($inputs: [TheatreMemberInput!]!) {
  registerTheatreMembers(inputs: $inputs) { ... }
}
```

**Required Permission:** `REGISTER_THEATRE_MEMBERS`

```graphql
input TheatreMemberInput {
  uid: String
  userUid: String
  firstName: String
  middleName: String
  lastName: String
  pfNumber: String
}
```

> **Note:** Unlike most inputs, TheatreMemberInput fields are all optional **except** that at least one identifying field should be provided.

---

## 6. Theatre Member Roles (assignment)

### Query: `getTheatreMemberRoles`

```graphql
query GetTheatreMemberRoles($pagination: PaginationInput!) {
  getTheatreMemberRoles(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        memberUid
        roleUid
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_THEATRE_MEMBER_ROLES`  
**Searchable fields:** `member_uid`, `role_uid`

**`TheatreMemberRoleNode` fields:**

| Field     | Type     | Description                   |
|-----------|----------|-------------------------------|
| uid       | String!  | Unique identifier             |
| memberUid | String!  | FK to TheatreMember           |
| roleUid   | String!  | FK to TheatreRole             |

### Mutation: `registerTheatreMemberRoles`

```graphql
mutation RegisterTheatreMemberRoles($inputs: [TheatreMemberRoleInput!]!) {
  registerTheatreMemberRoles(inputs: $inputs) { ... }
}
```

**Required Permission:** `REGISTER_THEATRE_MEMBER_ROLES`

```graphql
input TheatreMemberRoleInput {
  uid: String
  memberUid: String!
  roleUid: String!
}
```

---

## 7. Regions

### Query: `getRegions`

```graphql
query GetRegions($pagination: PaginationInput!) {
  getRegions(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_REGIONS`  
**Searchable fields:** `name`, `code`

**`RegionNode` fields:**

| Field | Type     | Description               |
|-------|----------|---------------------------|
| uid   | String!  | Unique identifier         |
| name  | String!  | Region name               |
| code  | String?  | Region code               |

### Query: `downloadRegionTemplate`

```graphql
query DownloadRegionTemplate {
  downloadRegionTemplate {
    status
    code
    message
    data {
      file_name
      base64_data
    }
  }
}
```

**Required Permission:** `VIEW_REGIONS`  
**Returns:** A base64-encoded `.xlsx` file (wrapped in `Response` envelope) with columns: `name`, `code`.

### Mutation: `registerRegions`

```graphql
mutation RegisterRegions($inputs: [RegionInput!]!) {
  registerRegions(inputs: $inputs) { ... }
}
```

```graphql
input RegionInput {
  uid: String
  name: String!
  code: String
}
```

### Mutation: `importRegionsFromExcel`

```graphql
mutation ImportRegionsFromExcel($fileInput: Base64ExcelInput!) {
  importRegionsFromExcel(fileInput: $fileInput) {
    status
    code
    message
    data {
      items { uid name code }
      totalCount
    }
  }
}
```

**Required Permission:** `REGISTER_REGIONS`  
**Input:** A `Base64ExcelInput` containing a base64-encoded Excel file matching the region template columns (`name`, `code`).  
**Note:** Returns `Response[RegionListNode]` (legacy pattern).

---

## 8. Internal Sources

### Query: `getInternalSources`

```graphql
query GetInternalSources($pagination: PaginationInput!) {
  getInternalSources(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_INTERNAL_SOURCES`  
**Searchable fields:** `name`, `code`

**`InternalSourceNode` fields:**

| Field | Type     | Description               |
|-------|----------|---------------------------|
| uid   | String!  | Unique identifier         |
| name  | String!  | Source name               |
| code  | String?  | Source code               |

### Query: `downloadInternalSourceTemplate`

```graphql
query DownloadInternalSourceTemplate {
  downloadInternalSourceTemplate {
    status
    code
    message
    data {
      file_name
      base64_data
    }
  }
}
```

**Required Permission:** `VIEW_INTERNAL_SOURCES`  
**Returns:** `Response[Base64ExcelOutput]` — A base64-encoded `.xlsx` file with columns: `name`, `code`.  
**Template columns:**

| Column | Width | Example           |
|--------|-------|-------------------|
| name   | 40    | Theatre Register  |
| code   | 20    | IS01              |

### Mutation: `registerInternalSources`

```graphql
mutation RegisterInternalSources($inputs: [InternalSourceInput!]!) {
  registerInternalSources(inputs: $inputs) { ... }
}
```

```graphql
input InternalSourceInput {
  uid: String
  name: String!
  code: String
}
```

### Mutation: `importInternalSourcesFromExcel`

```graphql
mutation ImportInternalSourcesFromExcel($fileInput: Base64ExcelInput!) {
  importInternalSourcesFromExcel(fileInput: $fileInput) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
      }
      totalCount
    }
  }
}
```

**Required Permission:** `REGISTER_INTERNAL_SOURCES`  
**Input:** `fileInput: Base64ExcelInput!` — A base64-encoded Excel file matching the template columns (`name`, `code`).  
**Returns:** `Response[InternalSourceListNode]` — The same list node returned by `getInternalSources`.

---

## 9. External Sources

### Query: `getExternalSources`

```graphql
query GetExternalSources($pagination: PaginationInput!) {
  getExternalSources(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
        regionUid
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_EXTERNAL_SOURCES`  
**Searchable fields:** `name`, `code`

**`ExternalSourceNode` fields:**

| Field     | Type     | Description                   |
|-----------|----------|-------------------------------|
| uid       | String!  | Unique identifier             |
| name      | String!  | Source name                   |
| code      | String?  | Source code                   |
| regionUid | String?  | FK to Region                  |

### Query: `downloadExternalSourceTemplate`

```graphql
query DownloadExternalSourceTemplate {
  downloadExternalSourceTemplate {
    status
    code
    message
    data {
      file_name
      base64_data
    }
  }
}
```

**Required Permission:** `VIEW_EXTERNAL_SOURCES`  
**Returns:** `Response[Base64ExcelOutput]` — A base64-encoded `.xlsx` file with columns: `name`, `code`, `region_uid`.  
**Template columns:**

| Column    | Width | Example               |
|-----------|-------|-----------------------|
| name      | 40    | Regional Hospital     |
| code      | 20    | ES01                  |
| region_uid| 36    | \<region-uuid-here\> |

### Mutation: `registerExternalSources`

```graphql
mutation RegisterExternalSources($inputs: [ExternalSourceInput!]!) {
  registerExternalSources(inputs: $inputs) { ... }
}
```

```graphql
input ExternalSourceInput {
  uid: String
  name: String!
  code: String
  regionUid: String
}
```

### Mutation: `importExternalSourcesFromExcel`

```graphql
mutation ImportExternalSourcesFromExcel($fileInput: Base64ExcelInput!) {
  importExternalSourcesFromExcel(fileInput: $fileInput) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
        regionUid
      }
      totalCount
    }
  }
}
```

**Required Permission:** `REGISTER_EXTERNAL_SOURCES`  
**Input:** `fileInput: Base64ExcelInput!` — A base64-encoded Excel file matching the template columns (`name`, `code`, `region_uid`).  
**Returns:** `Response[ExternalSourceListNode]` — The same list node returned by `getExternalSources`.

---

## 10. Theatre Units

### Query: `getTheatreUnits`

```graphql
query GetTheatreUnits($pagination: PaginationInput!) {
  getTheatreUnits(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
        location
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_THEATRE_UNITS`  
**Searchable fields:** `name`, `code`, `location`

**`TheatreUnitNode` fields:**

| Field    | Type     | Description               |
|----------|----------|---------------------------|
| uid      | String!  | Unique identifier         |
| name     | String!  | Unit name                 |
| code     | String?  | Unit code                 |
| location | String?  | Physical location         |

### Query: `downloadTheatreUnitTemplate`

```graphql
query DownloadTheatreUnitTemplate {
  downloadTheatreUnitTemplate {
    status
    code
    message
    data {
      file_name
      base64_data
    }
  }
}
```

**Required Permission:** `VIEW_THEATRE_UNITS`  
**Returns:** `Response[Base64ExcelOutput]` — A base64-encoded `.xlsx` file with columns: `name`, `code`, `location`.  
**Template columns:**

| Column   | Width | Example                    |
|----------|-------|----------------------------|
| name     | 40    | Main Operating Theatre     |
| code     | 20    | TU01                       |
| location | 30    | Block A, Floor 2           |

### Mutation: `registerTheatreUnits`

```graphql
mutation RegisterTheatreUnits($inputs: [TheatreUnitInput!]!) {
  registerTheatreUnits(inputs: $inputs) { ... }
}
```

```graphql
input TheatreUnitInput {
  uid: String
  name: String!
  code: String
  location: String
}
```

### Mutation: `importTheatreUnitsFromExcel`

```graphql
mutation ImportTheatreUnitsFromExcel($fileInput: Base64ExcelInput!) {
  importTheatreUnitsFromExcel(fileInput: $fileInput) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
        location
      }
      totalCount
    }
  }
}
```

**Required Permission:** `REGISTER_THEATRE_UNITS`  
**Input:** `fileInput: Base64ExcelInput!` — A base64-encoded Excel file matching the template columns (`name`, `code`, `location`).  
**Returns:** `Response[TheatreUnitListNode]` — The same list node returned by `getTheatreUnits`.

---

## 11. Death Reasons

### Query: `getDeathReasons`

```graphql
query GetDeathReasons($pagination: PaginationInput!) {
  getDeathReasons(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_DEATH_REASONS`  
**Searchable fields:** `name`, `code`

**`DeathReasonNode` fields:**

| Field | Type     | Description               |
|-------|----------|---------------------------|
| uid   | String!  | Unique identifier         |
| name  | String!  | Reason name               |
| code  | String?  | Reason code               |

### Query: `downloadDeathReasonTemplate`

```graphql
query DownloadDeathReasonTemplate {
  downloadDeathReasonTemplate {
    status
    code
    message
    data {
      file_name
      base64_data
    }
  }
}
```

**Required Permission:** `VIEW_DEATH_REASONS`  
**Returns:** `Response[Base64ExcelOutput]` — A base64-encoded `.xlsx` file with columns: `name`, `code`.  
**Template columns:**

| Column | Width | Example      |
|--------|-------|--------------|
| name   | 40    | Haemorrhage  |
| code   | 20    | DR01         |

### Mutation: `registerDeathReasons`

```graphql
mutation RegisterDeathReasons($inputs: [DeathReasonInput!]!) {
  registerDeathReasons(inputs: $inputs) { ... }
}
```

```graphql
input DeathReasonInput {
  uid: String
  name: String!
  code: String
}
```

### Mutation: `importDeathReasonsFromExcel`

```graphql
mutation ImportDeathReasonsFromExcel($fileInput: Base64ExcelInput!) {
  importDeathReasonsFromExcel(fileInput: $fileInput) {
    status
    code
    message
    data {
      items {
        uid
        name
        code
      }
      totalCount
    }
  }
}
```

**Required Permission:** `REGISTER_DEATH_REASONS`  
**Input:** `fileInput: Base64ExcelInput!` — A base64-encoded Excel file matching the template columns (`name`, `code`).  
**Returns:** `Response[DeathReasonListNode]` — The same list node returned by `getDeathReasons`.

---

## 12. Theatre Time Records (Core Entity)

### Query: `getTheatreTimeRecords`

```graphql
query GetTheatreTimeRecords($pagination: PaginationInput!) {
  getTheatreTimeRecords(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        patientMrn
        procedureDate
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_THEATRE_TIME_RECORDS`  
**Searchable fields:** `patient_mrn`, `patient_type`

**`TheatreTimeRecordNode` fields (note: currently only minimal fields exposed):**

| Field         | Type     | Description                    |
|---------------|----------|--------------------------------|
| uid           | String!  | Unique identifier              |
| patientMrn    | String?  | Patient Medical Record Number  |
| procedureDate | String?  | Procedure date                 |

> ⚠️ **Important:** The `TheatreTimeRecordNode` currently only exposes `uid`, `patientMrn`, and `procedureDate`. The full database model has many more fields (see DB model section below). If you need additional fields on the response, they must be added to the `TheatreTimeRecordNode` Strawberry type.

### Mutation: `registerTheatreTimeRecords`

```graphql
mutation RegisterTheatreTimeRecords($inputs: [TheatreTimeRecordInput!]!) {
  registerTheatreTimeRecords(inputs: $inputs) { ... }
}
```

**Required Permission:** `REGISTER_THEATRE_TIME_RECORDS`

```graphql
input TheatreTimeRecordInput {
  uid: String                    # Omit for create, provide for update
  patientMrn: String
  patientDob: String
  patientSex: String
  patientRegionUid: String       # FK -> Region
  patientType: String
  patientSourceType: String      # "INTERNAL" | "EXTERNAL"
  internalSourceUid: String      # FK -> InternalSource
  externalSourceUid: String      # FK -> ExternalSource
  theatreUnitUid: String         # FK -> TheatreUnit
  procedureUid: String           # FK -> Procedure
  procedureDate: String
}
```

### Database Model (TheatreTimeRecord) — Full Field Reference

The database model has these additional fields that may be added to the GraphQL type later:

| DB Column                      | Type     | Notes                              |
|--------------------------------|----------|------------------------------------|
| `procedure_start_time`         | Time     | Start time of procedure            |
| `procedure_end_time`           | Time     | End time of procedure              |
| `duration_minutes`             | Integer  | Calculated duration                |
| `estimated_procedure_minutes`  | Integer  | From Procedure reference           |
| `time_variance_minutes`        | Integer  | Difference (estimated vs actual)   |
| `surgery_met_time_between_cases` | String | Y/N flag                         |
| `was_there_delay`              | String   | Y/N flag                           |
| `surgery_beyond_theatre_time`  | String   | Y/N flag                           |
| `delay_cause_between_cases`    | Text     | Free text description              |
| `patient_outcome`              | String   | e.g. "DIED", "DISCHARGED", "TRANSFERRED" |
| `discharge_destination`        | String   | Discharge destination              |
| `discharge_internal_source_uid`| UUID     | FK -> InternalSource               |
| `death_reason_uid`             | UUID     | FK -> DeathReason                  |
| `death_description`            | Text     | Free text                          |
| `surgeon_name`                 | Text     | Free text                          |
| `anesthetist_name`             | Text     | Free text                          |
| `scrub_nurse_name`             | Text     | Free text                          |
| `runner_nurse_name`            | Text     | Free text                          |
| `created_by`                   | UUID     | User who created the record        |

---

## 13. Theatre Record Team Members

### Query: `getTheatreRecordTeamMembers`

```graphql
query GetTheatreRecordTeamMembers($pagination: PaginationInput!) {
  getTheatreRecordTeamMembers(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        recordUid
        memberUid
        roleUid
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_THEATRE_RECORD_TEAM_MEMBERS`  
**Searchable fields:** `record_uid`

**`TheatreRecordTeamMemberNode` fields:**

| Field     | Type     | Description                       |
|-----------|----------|-----------------------------------|
| uid       | String!  | Unique identifier                 |
| recordUid | String!  | FK -> TheatreTimeRecord           |
| memberUid | String!  | FK -> TheatreMember               |
| roleUid   | String!  | FK -> TheatreRole                 |

### Mutation: `registerTheatreRecordTeamMembers`

```graphql
mutation RegisterTheatreRecordTeamMembers($inputs: [TheatreRecordTeamMemberInput!]!) {
  registerTheatreRecordTeamMembers(inputs: $inputs) { ... }
}
```

**Required Permission:** `REGISTER_THEATRE_RECORD_TEAM_MEMBERS`

```graphql
input TheatreRecordTeamMemberInput {
  uid: String = null     # Optional for updates
  recordUid: String!     # FK -> TheatreTimeRecord
  memberUid: String!     # FK -> TheatreMember
  roleUid: String!       # FK -> TheatreRole
}
```

---

## 14. Theatre Record Delays

### Query: `getTheatreRecordDelays`

```graphql
query GetTheatreRecordDelays($pagination: PaginationInput!) {
  getTheatreRecordDelays(pagination: $pagination) {
    status
    code
    message
    data {
      items {
        uid
        recordUid
        procedureDelayCategoryUid
        delayCauseUid
        description
        sortOrder
      }
      totalCount
    }
  }
}
```

**Required Permission:** `VIEW_THEATRE_RECORD_DELAYS`  
**Searchable fields:** `description`

**`TheatreRecordDelayNode` fields:**

| Field                       | Type     | Description                           |
|-----------------------------|----------|---------------------------------------|
| uid                         | String!  | Unique identifier                     |
| recordUid                   | String!  | FK -> TheatreTimeRecord               |
| procedureDelayCategoryUid   | String?  | FK -> ProcedureDelayCategory          |
| delayCauseUid               | String?  | FK -> ProcedureDelayCause             |
| description                 | String?  | Free text description of the delay    |
| sortOrder                   | Int?     | Ordering of delays within a record    |

### Mutation: `registerTheatreRecordDelays`

```graphql
mutation RegisterTheatreRecordDelays($inputs: [TheatreRecordDelayInput!]!) {
  registerTheatreRecordDelays(inputs: $inputs) { ... }
}
```

**Required Permission:** `REGISTER_THEATRE_RECORD_DELAYS`

```graphql
input TheatreRecordDelayInput {
  uid: String
  recordUid: String!                     # FK -> TheatreTimeRecord
  procedureDelayCategoryUid: String      # FK -> ProcedureDelayCategory
  delayCauseUid: String                  # FK -> ProcedureDelayCause
  description: String
  sortOrder: Int
}
```

---

## Entity Relationship Diagram (High Level)

```
TheatreTimeRecord (core)
    ├── Procedure (surgery type)
    ├── TheatreUnit (room/OT)
    ├── TheatreRecordTeamMember (many)
    │       ├── TheatreMember (staff person)
    │       └── TheatreRole (role: Surgeon, Nurse, etc.)
    ├── TheatreRecordDelay (many)
    │       ├── ProcedureDelayCategory (e.g., "Equipment", "Staff")
    │       └── ProcedureDelayCause (e.g., "Broken light", "Missing scrub nurse")
    ├── Region (patient region)
    ├── InternalSource (referral from within hospital)
    ├── ExternalSource (referral from outside)
    │       └── Region
    └── DeathReason (if patient died)

TheatreMember <--> TheatreMemberRole (many-to-many via TheatreMemberRole)
    ├── TheatreMember
    └── TheatreRole
```

---

## Frontend GraphQL Client Usage Guide

### 1. General Request Shape

All requests are `POST` to `/graphql` with JSON body:

```json
{
  "query": "... mutation or query string ...",
  "variables": { ... }
}
```

Headers:
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### 2. Pagination Pattern (Applies to All Queries)

Every query uses the same pagination pattern. Example:

```javascript
// Frontend (e.g., Apollo Client / URQL / Relay)
const GET_ITEMS = gql`
  query GetItems($pagination: PaginationInput!) {
    getProcedureDelayCategories(pagination: $pagination) {
      status
      code
      message
      data {
        items { uid name code description }
        totalCount
      }
    }
  }
`;

// Variables
const variables = {
  pagination: {
    offset: 0,       // Page start index
    limit: 10,       // Page size
    search: "term"   // Optional search string
  }
};
```

### 3. Search Behavior

- The `search` field performs a **case-insensitive ILIKE** search across the defined searchable fields for each module.
- It matches **anywhere** in the string (not just prefix).
- If `search` is null/empty, all records are returned with pagination.

### 4. Batch Create/Update Pattern

All mutations accept a **list** of inputs, allowing batch operations:

```javascript
const REGISTER_MANY = gql`
  mutation RegisterItems($inputs: [ProcedureDelayCategoryInput!]!) {
    registerProcedureDelayCategories(inputs: $inputs) {
      status
      code
      message
      data { items { uid name } totalCount }
    }
  }
`;

// Create two new items
const variables = {
  inputs: [
    { name: "Equipment Delay", code: "EQ", description: "Delay due to equipment" },
    { name: "Staff Delay", code: "ST", description: "Delay due to staff unavailability" }
  ]
};
```

### 5. Update Existing Record

To update, pass the `uid` of the existing record along with the fields to change:

```javascript
const variables = {
  inputs: [
    { uid: "existing-uuid-here", name: "Updated Name" }
  ]
};
```

> **Note:** Only the provided fields are updated. Omitted fields remain unchanged.

### 6. Error Handling

Always check the `status` field and `code` in the response:

```javascript
const response = await client.query({ query, variables });
const { status, code, message, data } = response.data.getProcedureDelayCategories;

if (!status) {
  switch (code) {
    case 8003: // UNAUTHORIZED
      // Redirect to login
      break;
    case 8009: // RESTRICTED_ACCESS
      // Show "access denied" message
      break;
    case 8005: // FAILURE
      // Show generic error
      break;
    default:
      // Handle other codes
  }
}
```

### 7. Token Refresh

The backend validates JWT tokens. If a 401 is returned (UNAUTHORIZED - code 8003), the frontend should:
1. Attempt token refresh via the SSO endpoint (if available)
2. Retry the original request with the new token
3. If refresh fails, redirect to login

### 8. Downloading an Import Template

```javascript
const DOWNLOAD_TEMPLATE = gql`
  query DownloadTemplate {
    downloadDeathReasonTemplate {
      file_name
      base64_data
    }
  }
`;

// Decode and download the file
const response = await client.query({ query: DOWNLOAD_TEMPLATE });
const { file_name, base64_data } = response.data.downloadDeathReasonTemplate;
const binary = atob(base64_data);
const array = new Uint8Array(binary.length);
for (let i = 0; i < binary.length; i++) array[i] = binary.charCodeAt(i);
const blob = new Blob([array], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" });
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = file_name;
a.click();
```

### 9. Importing from Excel

```javascript
// Read a file, encode to base64, then send
const file = fileInput.files[0];
const reader = new FileReader();
reader.onload = () => {
  const base64 = reader.result.split(",")[1]; // Remove data:...;base64, prefix
  const variables = {
    input: {
      file_name: file.name,
      base64_data: base64
    }
  };
  client.mutate({
    mutation: IMPORT_MUTATION,
    variables
  }).then(result => {
    const { imported, duplicates, failed, details } = result.data.importDeathReasonsFromExcel;
    console.log(`Imported: ${imported}, Duplicates: ${duplicates}, Failed: ${failed}`);
  });
};
reader.readAsDataURL(file);
```

---

## Summary: Complete Field List by Module

| Module                    | Query Field                                | Mutation Field                                      | Download Template                                   | Import from Excel                                    |
|---------------------------|--------------------------------------------|-----------------------------------------------------|-----------------------------------------------------|------------------------------------------------------|
| ProcedureDelayCategories  | `getProcedureDelayCategories`              | `registerProcedureDelayCategories`                  | `downloadProcedureDelayCategoryTemplate`            | `importProcedureDelayCategoriesFromExcel`            |
| ProcedureDelayCauses      | `getProcedureDelayCauses`                  | `registerProcedureDelayCauses`                      | —                                                   | —                                                    |
| Procedures                | `getProcedures`                            | `registerProcedures`                                | —                                                   | —                                                    |
| TheatreRoles              | `getTheatreRoles`                          | `registerTheatreRoles`                              | —                                                   | —                                                    |
| TheatreMembers            | `getTheatreMembers`                        | `registerTheatreMembers`                            | —                                                   | —                                                    |
| TheatreMemberRoles        | `getTheatreMemberRoles`                    | `registerTheatreMemberRoles`                        | —                                                   | —                                                    |
| Regions                   | `getRegions`                               | `registerRegions`                                   | `downloadRegionTemplate`                            | `importRegionsFromExcel`                             |
| InternalSources           | `getInternalSources`                       | `registerInternalSources`                           | `downloadInternalSourceTemplate`                    | `importInternalSourcesFromExcel`                     |
| ExternalSources           | `getExternalSources`                       | `registerExternalSources`                           | `downloadExternalSourceTemplate`                    | `importExternalSourcesFromExcel`                     |
| TheatreUnits              | `getTheatreUnits`                          | `registerTheatreUnits`                              | `downloadTheatreUnitTemplate`                       | `importTheatreUnitsFromExcel`                        |
| DeathReasons              | `getDeathReasons`                          | `registerDeathReasons`                              | `downloadDeathReasonTemplate`                       | `importDeathReasonsFromExcel`                        |
| TheatreTimeRecords        | `getTheatreTimeRecords`                    | `registerTheatreTimeRecords`                        | —                                                   | —                                                    |
| TheatreRecordTeamMembers  | `getTheatreRecordTeamMembers`              | `registerTheatreRecordTeamMembers`                  | —                                                   | —                                                    |
| TheatreRecordDelays       | `getTheatreRecordDelays`                   | `registerTheatreRecordDelays`                       | —                                                   | —                                                    |

> **Legend:** `—` means the module does **not** have a download-template or import-from-excel endpoint (typically used for entities with complex FK relationships or non-bulk operations).