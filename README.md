# PadelGo - Complete Padel Club Management Platform

A comprehensive full-stack application for managing padel clubs, tournaments, and player communities. Built with modern web technologies and deployed on Railway.

## 🏓 What is PadelGo?

PadelGo is a complete digital platform that connects padel players with clubs while providing powerful management tools for club administrators. Whether you're a player looking to book courts, join tournaments, or track your progress, or a club owner needing to manage facilities and events, PadelGo has you covered.

## ✨ Key Features

### For Players
- **🏟️ Club Discovery**: Browse and discover padel clubs in your area
- **📅 Court Booking**: Book courts with real-time availability
- **🎮 Game Management**: Create private games or join public matches
- **👥 Team Formation**: Create and manage competitive teams
- **🏆 Tournament Participation**: Join tournaments with ELO-based skill categories
- **📊 Performance Tracking**: Monitor your ELO rating and view personal statistics
- **🏅 Achievement System**: Earn trophies and badges for tournament victories
- **📱 Social Features**: Invite friends and build your padel community

### For Club Administrators
- **🏢 Club Management**: Complete club profile and facility management
- **🎾 Court Administration**: Add, edit, and manage court availability
- **📋 Booking Overview**: View and manage all club bookings
- **🏆 Tournament Creation**: Organize tournaments with automated bracket generation
- **📈 Analytics Dashboard**: Track club performance and user engagement
- **⚙️ Schedule Management**: Manage court schedules and operational hours
- **👨‍💼 Multi-Admin Support**: Collaborate with other club administrators

## 🏗️ Architecture

PadelGo is built using a **monorepo architecture** with three main applications:

```
PadelGo/
├── padel-app/
│   ├── apps/
│   │   ├── api/           # FastAPI Backend
│   │   ├── web/           # Player-facing Next.js App
│   │   └── club-admin/    # Club Admin Portal
│   └── packages/
│       └── ui/            # Shared UI Components
```

### Backend (`api`)
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Migrations**: Alembic for database schema management
- **File Storage**: Cloudinary for image uploads
- **API Documentation**: Automatic OpenAPI/Swagger documentation

### Frontend Applications
- **Framework**: Next.js with TypeScript
- **UI Components**: shadcn/ui component library
- **Styling**: Tailwind CSS
- **State Management**: React Context API + React Query
- **Form Handling**: React Hook Form with Zod validation
- **Testing**: Jest + Cypress for E2E testing

### Shared Infrastructure
- **Monorepo Management**: pnpm workspaces with Turbo
- **Code Quality**: ESLint, Prettier, TypeScript strict mode
- **CI/CD**: Automated testing and deployment
- **Cloud Platform**: Railway for hosting all services

## 🚀 Advanced Features

### Tournament System
- **ELO-based Categories**: Bronze, Silver, Gold, Platinum divisions
- **Automated Bracket Generation**: Single-elimination tournaments
- **Match Scheduling**: Integrated court booking for matches
- **Achievement System**: Trophies and badges for winners
- **Team Registration**: Eligibility verification based on ELO ratings

### ELO Rating System
- **Skill-based Matching**: Players matched by skill level
- **Dynamic Ratings**: Real-time updates after each match
- **Historical Tracking**: Complete rating history and statistics
- **Leaderboards**: Club and global ranking systems
- **Manual Adjustments**: Admin-approved rating corrections

### Enhanced Game Management
- **Public Games**: Open slots for community participation
- **Private Games**: Invitation-only matches
- **Smart Expiration**: Automatic cleanup of inactive games
- **Result Tracking**: Comprehensive match statistics
- **Team Gameplay**: Partner matching and team statistics

## 🛠️ Getting Started

### Prerequisites
- Node.js (>= 20.0.0)
- Python (>= 3.11)
- pnpm (>= 8.0.0)
- PostgreSQL database
- Cloudinary account (for image uploads)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tarikstafford/PadelApp.git
   cd PadelApp
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Set up environment variables:**
   Create a `.env` file in `padel-app/apps/api/` with:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/padelgo
   SECRET_KEY=your-secret-key-here
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```

4. **Set up the database:**
   ```bash
   cd padel-app/apps/api
   alembic upgrade head
   ```

5. **Start the development servers:**
   ```bash
   # Backend API (runs on port 8000)
   pnpm --filter api run dev

   # Player web app (runs on port 3000)
   pnpm --filter web run dev

   # Club admin portal (runs on port 3001)
   pnpm --filter club-admin run dev
   ```

## 🧪 Testing

### Running Tests
```bash
# Backend tests
cd padel-app/apps/api
python -m pytest

# Frontend tests
pnpm --filter web test
pnpm --filter club-admin test

# E2E tests
pnpm --filter club-admin cy:run
```

### Test Coverage
- **Backend**: Comprehensive API endpoint and service testing
- **Frontend**: Component testing with React Testing Library
- **E2E**: Critical user flows with Cypress

## 🚢 Deployment

The application is deployed on Railway with the following services:

- **API**: Python FastAPI service with PostgreSQL database
- **Web App**: Next.js application with static optimization
- **Club Admin**: Next.js application with admin-specific features

### Production Configuration
- **Environment**: Railway managed environment variables
- **Database**: PostgreSQL with connection pooling
- **CDN**: Cloudinary for image delivery
- **SSL**: Automatic HTTPS with Railway

## 📝 API Documentation

The API documentation is automatically generated and available at:
- **Development**: `http://localhost:8000/docs`
- **Production**: `https://your-api-domain.railway.app/docs`

### Key API Endpoints
- `/auth/*` - Authentication and user management
- `/clubs/*` - Club information and management
- `/courts/*` - Court availability and booking
- `/games/*` - Game creation and management
- `/tournaments/*` - Tournament system
- `/admin/*` - Administrative functions

## 📚 Project Structure

```
PadelGo/
├── documentation/          # Project documentation
├── padel-app/
│   ├── apps/
│   │   ├── api/           # FastAPI Backend
│   │   │   ├── app/
│   │   │   │   ├── models/      # Database models
│   │   │   │   ├── schemas/     # Pydantic schemas
│   │   │   │   ├── routers/     # API endpoints
│   │   │   │   ├── crud/        # Database operations
│   │   │   │   ├── services/    # Business logic
│   │   │   │   └── utils/       # Utility functions
│   │   │   ├── migrations/      # Database migrations
│   │   │   └── tests/          # API tests
│   │   ├── web/           # Player Web App
│   │   │   ├── app/            # Next.js app router
│   │   │   ├── components/     # React components
│   │   │   ├── contexts/       # React contexts
│   │   │   ├── hooks/          # Custom hooks
│   │   │   └── lib/            # Utilities
│   │   └── club-admin/    # Club Admin Portal
│   │       ├── app/            # Next.js app router
│   │       ├── components/     # Admin components
│   │       ├── contexts/       # Admin contexts
│   │       ├── hooks/          # Admin hooks
│   │       └── cypress/        # E2E tests
│   └── packages/
│       └── ui/            # Shared UI components
├── scripts/               # Utility scripts
└── tests/                # Integration tests
```

## 🤝 Contributing

We welcome contributions to PadelGo! Please read our contributing guidelines and follow our code of conduct.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

### Code Quality
- TypeScript strict mode enabled
- ESLint and Prettier for code formatting
- Comprehensive test coverage required
- API documentation must be updated

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **shadcn/ui** for the beautiful component library
- **FastAPI** for the high-performance backend framework
- **Next.js** for the powerful React framework
- **Railway** for simplified deployment and hosting

---

**Built with ❤️ for the padel community**
