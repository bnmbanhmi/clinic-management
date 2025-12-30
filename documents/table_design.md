[backend.png](https://drive.google.com/open?id=1aJ3r8Al-QQi2u6VH3KEAF-luhXLCFSp8)

# **Backend Table Design \- Clinic Management System**

## **User**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| user\_id | INT | No | PK | Unique identifier |
| email | VARCHAR | No | UNIQUE | Login email |
| full\_name | VARCHAR | No |  | Full name |
| hashed\_password | VARCHAR | No |  | Password hashed |
| role | VARCHAR | No | CHECK | User role |

## **Patient**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| patient\_id | INT | No | PK | Identifier |
| user\_id | INT | No | FK | Link to user |
| date\_of\_birth | DATE | No |  | Birthdate |
| gender | VARCHAR | No |  | Gender |
| address | VARCHAR | Yes |  | Address |
| phone | VARCHAR | Yes |  | Phone |

## **Doctor**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| doctor\_id | INT | No | PK | Identifier |
| user\_id | INT | No | FK | User link |
| specialization | VARCHAR | No |  | Specialty |
| description | TEXT | Yes |  | Description |
| hospital\_id | INT | No | FK | Hospital link |

## **Staff**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| staff\_id | INT | No | PK | Identifier |
| user\_id | INT | No | FK | User link |
| position | VARCHAR | No |  | Position |

## **Hospital**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| hospital\_id | INT | No | PK | Identifier |
| name | VARCHAR | No |  | Hospital name |
| address | VARCHAR | No |  | Address |

## **Appointment**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| appointment\_id | INT | No | PK | Identifier |
| patient\_id | INT | No | FK | Patient link |
| doctor\_id | INT | No | FK | Doctor link |
| service | VARCHAR | No |  | Service |
| appointment\_date | DATE | No |  | Date |
| appointment\_time | TIME | No |  | Time |
| status | VARCHAR | No | CHECK | Status |

## **MedicalReport**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| report\_id | INT | No | PK | Identifier |
| patient\_id | INT | No | FK | Patient link |
| doctor\_id | INT | No | FK | Doctor link |
| appointment\_id | INT | Yes | FK | Appointment link |
| notes | TEXT | Yes |  | Notes |
| diagnosis | VARCHAR | Yes |  | Diagnosis |
| created\_at | DATETIME | No |  | Created time |

## **Prescription**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| prescription\_id | INT | No | PK | Identifier |
| report\_id | INT | No | FK | Medical report |
| medication\_name | VARCHAR | No |  | Medicine |
| dosage | VARCHAR | No |  | Dosage |
| quantity | INT | No |  | Quantity |

## **ChatMessage**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| message\_id | INT | No | PK | Identifier |
| user\_id | INT | No | FK | User link |
| content | TEXT | No |  | Content |
| role | VARCHAR | No | CHECK | Role |
| timestamp | DATETIME | No |  | Time sent |

## **OTCMedicationRecord**

| Field | Data Type | Nullable | Constraint | Description |
| :---- | :---- | :---- | :---- | :---- |
| otc\_id | INT | No | PK | Identifier |
| patient\_id | INT | No | FK | Patient link |
| staff\_id | INT | No | FK | Staff link |
| medication\_name | VARCHAR | No |  | Medicine |
| quantity | INT | No |  | Quantity |
| created\_at | DATETIME | No |  | Created time |

[frontend.png](https://drive.google.com/open?id=1w-EZt7Gm4XBWgChCIVf41d3cEAvMlTeB)

# **Frontend Table Design \- Clinic Management System**

## **Sidebar**

| Field | Type | Description |
| :---- | :---- | :---- |
| navigate() | function | Navigate to selected page |

## **Navbar**

| Field | Type | Description |
| :---- | :---- | :---- |
| showUser() | function | Display logged-in user's info |

## **AppointmentCard**

| Field | Type | Description |
| :---- | :---- | :---- |
| renderInfo() | function | Show appointment details |

## **AppointmentList**

| Field | Type | Description |
| :---- | :---- | :---- |
| renderList() | function | Render list of appointments |

## **AppointmentForm**

| Field | Type | Description |
| :---- | :---- | :---- |
| handleSubmit() | function | Submit appointment form |

## **MedicalRecordForm**

| Field | Type | Description |
| :---- | :---- | :---- |
| handleSubmit() | function | Submit medical record form |

## **ChatBox**

| Field | Type | Description |
| :---- | :---- | :---- |
| handleSend() | function | Send chat message |

## **ChatMessageItem**

| Field | Type | Description |
| :---- | :---- | :---- |
| render() | function | Render chat message block |

## **ProfileForm**

| Field | Type | Description |
| :---- | :---- | :---- |
| saveProfile() | function | Save profile changes |

## **LoadingSpinner**

| Field | Type | Description |
| :---- | :---- | :---- |
|  | component | Displays loading animation |

## **LoginPage**

| Field | Type | Description |
| :---- | :---- | :---- |
| handleLogin() | function | Login user |

## **RegisterPage**

| Field | Type | Description |
| :---- | :---- | :---- |
| handleRegister() | function | Register new user |

## **DashboardPage**

| Field | Type | Description |
| :---- | :---- | :---- |
| loadDashboard() | function | Load dashboard data |
| loadAppointments() | function | Load appointments |

## **PatientProfilePage**

| Field | Type | Description |
| :---- | :---- | :---- |
| loadProfile() | function | Load profile |
| saveProfile() | function | Save profile |

## **DoctorSchedulePage**

| Field | Type | Description |
| :---- | :---- | :---- |
| loadAppointments() | function | Load schedule |

## **AppointmentPage**

| Field | Type | Description |
| :---- | :---- | :---- |
| submitAppointment() | function | Submit new appointment |

## **AppointmentDetailPage**

| Field | Type | Description |
| :---- | :---- | :---- |
| loadDetail() | function | Load detail |

## **MedicalRecordPage**

| Field | Type | Description |
| :---- | :---- | :---- |
| loadRecords() | function | Load list of records |

## **MedicalRecordDetailPage**

| Field | Type | Description |
| :---- | :---- | :---- |
| loadRecord() | function | Load single record |

## **ChatbotPage**

| Field | Type | Description |
| :---- | :---- | :---- |
| loadHistory() | function | Load chat history |
| sendMessage() | function | Send chat message |

## **AuthService**

| Field | Type | Description |
| :---- | :---- | :---- |
| login() | API call | User login |
| register() | API call | Register user |
| logout() | function | Logout user |

## **UserService**

| Field | Type | Description |
| :---- | :---- | :---- |
| getUserInfo() | API call | Fetch user data |
| updateProfile() | API call | Update profile |

## **AppointmentService**

| Field | Type | Description |
| :---- | :---- | :---- |
| book() | API call | Create appointment |
| getAll() | API call | Get appointments |
| getById() | API call | Get detail |
| update() | API call | Update appointment |

## **MedicalRecordService**

| Field | Type | Description |
| :---- | :---- | :---- |
| getRecords() | API call | Fetch all records |
| getRecordById() | API call | Fetch detail |
| createRecord() | API call | Create record |

## **ChatService**

| Field | Type | Description |
| :---- | :---- | :---- |
| sendMessage() | API call | Send chat |
| getHistory() | API call | Load history |

## **useAuth**

| Field | Type | Description |
| :---- | :---- | :---- |
| user | object | Current user |
| login() | function | Login |
| logout() | function | Logout |

## **useAppointments**

| Field | Type | Description |
| :---- | :---- | :---- |
| appointments | array | Appointment list |
| loadAppointments() | function | Load list |

## **useMedicalRecords**

| Field | Type | Description |
| :---- | :---- | :---- |
| records | array | Record list |
| loadRecords() | function | Load records |

## **useChat**

| Field | Type | Description |
| :---- | :---- | :---- |
| messages | array | Chat messages |
| sendMessage() | function | Send a message |

## **useProfile**

| Field | Type | Description |
| :---- | :---- | :---- |
| profile | object | Profile |
| saveProfile() | function | Save profile |

## **UserType**

| Field | Type | Description |
| :---- | :---- | :---- |
| user\_id | number | ID |
| email | string | Email |
| full\_name | string | Full name |
| role | string | Role |

## **PatientType**

| Field | Type | Description |
| :---- | :---- | :---- |
| patient\_id | number | ID |
| gender | string | Gender |
| address | string | Address |
| phone | string | Phone |

## **DoctorType**

| Field | Type | Description |
| :---- | :---- | :---- |
| doctor\_id | number | ID |
| specialization | string | Specialty |
| description | string | Description |

## **AppointmentType**

| Field | Type | Description |
| :---- | :---- | :---- |
| appointment\_id | number | ID |
| service | string | Service |
| appointment\_date | string | Date |
| appointment\_time | string | Time |
| status | string | Status |

## **MedicalRecordType**

| Field | Type | Description |
| :---- | :---- | :---- |
| record\_id | number | ID |
| notes | string | Notes |
| diagnosis | string | Diagnosis |

## **ChatMessageType**

| Field | Type | Description |
| :---- | :---- | :---- |
| message\_id | number | ID |
| content | string | Content |
| role | string | Role |
| timestamp | string | Timestamp |
