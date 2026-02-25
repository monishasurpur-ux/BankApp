# KodBank - Banking Application Specification

## Project Overview
- **Project Name**: KodBank
- **Type**: Full-stack Web Application (Flask + HTML/CSS/JS)
- **Core Functionality**: A banking application with user registration, login, balance check, and money transfer features
- **Target Users**: Bank customers who need to manage their accounts online

## Technical Stack
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Authentication**: JWT Tokens (stored in localStorage)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key, Auto-increment |
| userid | TEXT | Unique user identifier |
| email | TEXT | User email (unique) |
| phone | TEXT | Phone number |
| password | TEXT | Hashed password |
| full_name | TEXT | Full name of user |
| balance | REAL | Account balance (default: 10000) |
| created_at | DATETIME | Account creation timestamp |

### Transactions Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key, Auto-increment |
| from_userid | TEXT | Sender userid |
| to_userid | TEXT | Receiver userid |
| amount | REAL | Transfer amount |
| timestamp | DATETIME | Transaction timestamp |

## UI/UX Specification

### Color Palette
- **Primary**: #1a1a2e (Deep Navy)
- **Secondary**: #16213e (Dark Blue)
- **Accent**: #e94560 (Coral Red)
- **Success**: #00d9a5 (Mint Green)
- **Background**: #0f0f1a (Dark Background)
- **Card Background**: #1f1f3a (Dark Purple-Gray)
- **Text Primary**: #ffffff (White)
- **Text Secondary**: #a0a0b0 (Light Gray)

### Typography
- **Font Family**: 'Outfit' (Google Fonts) - Modern geometric sans-serif
- **Headings**: 700 weight
- **Body**: 400 weight
- **Sizes**: 
  - H1: 2.5rem
  - H2: 1.75rem
  - Body: 1rem
  - Small: 0.875rem

### Layout Structure
- **Header**: Logo (left), Navigation (right - Home, Balance, Transfer, Logout)
- **Main Content**: Centered card-based layout
- **Responsive**: Mobile-first design, max-width 480px for cards

### Pages

#### 1. Login Page
- Logo and title
- Email/UserID input
- Password input
- "Login" button
- "Don't have an account? Register" link
- Error message display area

#### 2. Registration Page
- Logo and title
- Full Name input
- UserID input (unique)
- Email input
- Phone Number input
- Password input
- Confirm Password input
- "Register" button
- "Already have an account? Login" link
- Success/Error message display area

#### 3. Dashboard (After Login)
- Welcome message with user name
- Quick balance display card
- Quick action buttons (Check Balance, Transfer)
- Recent transactions list (last 5)
- Logout button

#### 4. Balance Page
- Current balance display (large, prominent)
- "Refresh" button
- "Go to Dashboard" button
- Requires authentication

#### 5. Transfer Money Page
- Recipient UserID input
- Amount input
- "Transfer" button
- Confirmation modal
- Success/Error message display
- Requires authentication

### Animations & Effects
- Page transitions: Fade in (0.3s ease)
- Button hover: Scale 1.02, brightness increase
- Card hover: Subtle shadow increase
- Input focus: Border color change to accent
- Loading spinner for async operations
- Success/Error toast notifications

## Functionality Specification

### Authentication Flow
1. **Registration**:
   - Validate all fields are filled
   - Check if email/userid already exists
   - Hash password using bcrypt
   - Create new user with default balance (10000)
   - Return success/error message

2. **Login**:
   - Validate credentials
   - Generate JWT token
   - Store token in localStorage
   - Redirect to dashboard

3. **Protected Routes**:
   - Check for valid JWT token
   - Decode token to get userid
   - Return 401 if invalid/expired

### Balance Check
- Requires authentication
- Fetch user's current balance from database
- Display balance prominently
- Show last 5 transactions

### Money Transfer
- Requires authentication
- Validate recipient exists
- Validate sufficient balance
- Validate amount > 0
- Create transaction record
- Update both sender and recipient balances
- Return success/failure message

### Logout
- Clear localStorage token
- Redirect to login page

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /api/register | Register new user | No |
| POST | /api/login | Login user | No |
| GET | /api/balance | Get user balance | Yes |
| POST | /api/transfer | Transfer money | Yes |
| GET | /api/transactions | Get user transactions | Yes |

## Acceptance Criteria

### Registration
- [ ] All fields are required
- [ ] Email must be valid format
- [ ] UserID must be unique
- [ ] Password minimum 6 characters
- [ ] Success redirects to login

### Login
- [ ] Valid credentials return success
- [ ] Invalid credentials show error
- [ ] Token stored in localStorage
- [ ] Redirects to dashboard on success

### Balance Check
- [ ] Shows current balance
- [ ] Requires authentication
- [ ] Shows error if not logged in

### Transfer Money
- [ ] Validates recipient exists
- [ ] Checks sufficient balance
- [ ] Updates both accounts
- [ ] Creates transaction record
- [ ] Shows confirmation

### UI/UX
- [ ] Responsive design works on mobile
- [ ] Smooth animations
- [ ] Clear error messages
- [ ] Loading states shown
- [ ] Logout clears session
