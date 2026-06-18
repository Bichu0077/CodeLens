# CodeLens 🎯

> An intelligent, real-time coding practice platform with sandboxed execution and AI-powered hints.

![Python](https://img.shields.io/badge/Python-3.11+-3776ab?logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18.3+-61dafb?logo=react&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ed?logo=docker&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-green)

## 📋 Overview

CodeLens is a **competitive coding platform** designed for learning, featuring:
- **Sandboxed Python execution** with strict resource limits (memory, CPU, timeout)
- **Real-time test result streaming** via WebSocket for instant feedback
- **Grounded AI hints** (3-level escalation) powered by Groq LLM
- **Production-ready architecture** with async/await, PostgreSQL, and Docker isolation

Unlike generic coding platforms, CodeLens prioritizes **pedagogical design**: hints are grounded in actual failures, not generic advice. A student sees "your loop doesn't handle empty input" instead of "think about edge cases."

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (React 18 + TypeScript + Vite)                        │
│  • Monaco Editor (VS Code embedded)                              │
│  • Real-time WebSocket subscription                              │
│  • Auth with JWT + localStorage                                  │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTP/HTTPS + WebSocket
┌────────────────▼────────────────────────────────────────────────┐
│  Backend (FastAPI + AsyncIO)                                     │
│  • Async endpoints (no request blocking)                         │
│  • Docker sandbox manager                                        │
│  • Groq LLM integration (hint generation)                         │
│  • PostgreSQL + SQLAlchemy ORM                                   │
└────────────────┬────────────────────────────────────────────────┘
                 │ AsyncPG (async driver)
┌────────────────▼────────────────────────────────────────────────┐
│  Database (PostgreSQL 16)                                        │
│  • Users, Problems, Submissions, Hints                           │
│  • JSON columns for flexible test storage                        │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Docker Sandboxing** | Bulletproof security (no network, memory capped, SIGKILL after 10s) | ~1-2s overhead per submission |
| **WebSocket Streaming** | Results appear as they complete (real-time feel) | Stateful connection management |
| **Groq LLM** | Fast inference for low-latency hints | Less capable than GPT-4 |
| **Async/Await** | Handle 100s of concurrent submissions | Requires async-compatible libraries |
| **PostgreSQL JSON** | Flexible test case schema without migrations | Less queryable than normalization |

---

## ✨ Features

### 🧠 Intelligent Hint System
Three-level escalation based on learning pedagogy:
- **Level 1** (Nudge): "What happens when the input is empty?"
- **Level 2** (Specific): "Your loop doesn't handle empty arrays. Consider the edge case."
- **Level 3** (Near-Solution): "You need a hash map to track seen numbers. Try storing index along with value."

Hints are **grounded in actual failures**:
```python
Failing test:
  Input:    [2, 7], target=5
  Expected: []
  Actual:   [0, 1]
  Error:    None

LLM receives: code + test case + prior hints → generates targeted hint
```

### ⚡ Real-Time Execution
```
User submits code
    ↓
WebSocket connects
    ↓
Backend spins up Docker container (fresh, isolated)
    ↓
Run test 1 → stream result {passed, input, expected, actual, ms}
    ↓
Run test 2 → stream result
    ↓
Run test 3 → stream result
    ↓
WebSocket closes (all tests complete)
```

**Result**: UI renders each test result instantly (not waiting for all tests to finish).

### 🔒 Sandboxed Execution

Each submission runs in a **containerized Python environment**:
```dockerfile
docker run --rm \
  --memory=128m \              # Memory limit
  --cpus=0.5 \                 # CPU quota (50%)
  --network=none \             # No network access
  --read-only \                # Read-only filesystem
  --user=1000 \                # Non-root user
  python:3.11-slim \
  python -c "# user code"
```

**Security guarantees**:
- ✅ No network access (can't exfiltrate data)
- ✅ Memory bounded (can't allocate infinite RAM)
- ✅ CPU bounded (can't DoS the host)
- ✅ Timeout enforced (SIGKILL after 10s)
- ✅ Filesystem isolated (no access to host files)

### 📊 Test Case Management
- **Public tests** shown in the UI (practice reference)
- **Hidden tests** run server-side (actual validation)
- Per-test timing metrics
- Detailed pass/fail/error reporting

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- PostgreSQL 16 (or use compose-provided image)
- Python 3.11+
- Node.js 18+

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/Bichu0077/CodeLens.git
cd CodeLens

# 2. Set environment variables
cp .env.example .env
# Edit .env with your Groq API key (get free key at groq.com)
export GROQ_API_KEY=your_key_here

# 3. Start services
docker-compose up

# 4. Visit the app
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs (Swagger UI)
```

### Stopping Services
```bash
docker-compose down
# Remove volumes with: docker-compose down -v
```

---

## 📁 Project Structure

```
CodeLens/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app setup, CORS, routing
│   │   ├── config.py            # Settings (env vars)
│   │   ├── database.py          # SQLAlchemy setup, async session
│   │   ├── models.py            # User, Problem, Submission, Hint
│   │   ├── schemas.py           # Pydantic request/response models
│   │   ├── routes/
│   │   │   ├── auth.py          # Register, login, JWT endpoints
│   │   │   ├── problems.py      # List, get problems (public/hidden test filtering)
│   │   │   └── submissions.py   # Create, stream, hint generation
│   │   └── services/
│   │       ├── executor.py      # Docker sandbox (run_tests_streamed)
│   │       ├── hint.py          # Groq LLM integration (generate_hint)
│   │       └── auth_utils.py    # JWT, password hashing
│   ├── Dockerfile               # Python 3.11-slim, Uvicorn
│   └── requirements.txt          # FastAPI, SQLAlchemy, Docker, Groq, etc.
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx             # React entry point
│   │   ├── api.ts               # Axios client + JWT interceptor
│   │   ├── AuthContext.tsx      # User auth state (Context API)
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/
│   │   │   ├── Login.tsx        # Email/password auth
│   │   │   ├── Register.tsx     # User signup
│   │   │   ├── Dashboard.tsx    # Problem list view
│   │   │   └── Problem.tsx      # Code editor, test results, hints
│   │   ├── hooks/
│   │   │   └── useSubmissionWS.ts  # WebSocket subscription hook
│   │   └── types/
│   │       └── index.ts         # TypeScript interfaces
│   ├── Dockerfile               # Node 18, Vite build + dev server
│   ├── vite.config.ts           # Vite bundler config
│   └── package.json             # React, Axios, Monaco, React Router
│
├── docker-compose.yml           # PostgreSQL + backend + frontend orchestration
└── README.md                    # This file
```

---

## 🔧 Tech Stack

### Backend
| Layer | Technology | Why |
|-------|-----------|-----|
| **Framework** | FastAPI | Modern, async-first, auto OpenAPI docs |
| **Server** | Uvicorn | ASGI, production-ready |
| **Database** | PostgreSQL | Relational, JSON support, battle-tested |
| **ORM** | SQLAlchemy 2.0 | Async support, type hints, relationship management |
| **Auth** | JWT (python-jose) | Stateless, scalable |
| **Execution** | Docker | Security isolation, resource limits |
| **LLM** | Groq | Fast inference, cheap |
| **WebSocket** | websockets | Real-time streaming |

### Frontend
| Layer | Technology | Why |
|-------|-----------|-----|
| **Framework** | React 18 | Component reusability, hooks |
| **Language** | TypeScript | Type safety, IDE autocomplete |
| **Build** | Vite | Fast HMR, modern bundler |
| **Editor** | Monaco Editor | Professional UX (VS Code experience) |
| **Routing** | React Router v6 | Client-side SPA navigation |
| **HTTP** | Axios | Promise-based, interceptors (JWT injection) |
| **Styling** | CSS Modules / Tailwind | Component-scoped styles |

---

## 📚 API Endpoints

### Authentication
```bash
POST /auth/register
POST /auth/login
POST /auth/refresh
```

### Problems
```bash
GET  /problems/              # List all problems (sorted by difficulty)
GET  /problems/{slug}        # Get problem details + public tests
```

### Submissions
```bash
POST /submissions/                    # Create submission, returns submission_id
WS   /submissions/ws/{submission_id}  # Subscribe to real-time test results
POST /submissions/{id}/hint           # Generate AI hint (level 1-3)
PUT  /submissions/{id}/hint/{hint_id}/feedback  # Record hint helpfulness
```

**Example: Submit code and stream results**
```javascript
// Create submission
const res = await api.post('/submissions/', {
  problem_id: 'abc123',
  code: 'def solution(nums):\n    return nums'
});
const submissionId = res.data.id;

// Connect WebSocket
const ws = new WebSocket(`ws://localhost:8000/submissions/ws/${submissionId}`);
ws.onmessage = (event) => {
  const testResult = JSON.parse(event.data);
  // {
  //   "index": 0,
  //   "status": "passed",
  //   "input": "[1, 2, 3]",
  //   "expected": "6",
  //   "actual": "6",
  //   "elapsed_ms": 2.34
  // }
};
```

---

## 🔐 Security Considerations

### Code Execution Isolation
- **No network**: `--network=none` (can't phone home)
- **Memory bounded**: 128MB (can't OOM the host)
- **CPU limited**: 50% of one core (can't hog resources)
- **Hard timeout**: 10 seconds then SIGKILL
- **Read-only filesystem**: No file modifications
- **Non-root user**: Reduced privilege escalation risk

### API Security
- **JWT expiry**: 24 hours
- **Password hashing**: bcrypt (not plaintext)
- **CORS configured**: Restricted origins (dev: localhost only)
- **Test case filtering**: Hidden tests never sent to frontend
- **Secrets in env vars**: Not hardcoded (use `.env`)

### Data Protection
- PII (email, password): Hashed before storage
- User code: Stored in DB (needed for hints), never logged
- LLM prompts: Include only necessary context (not full DB)

---

## 🧪 Testing & Quality

### Current Coverage
- ✅ Manual testing (local docker-compose setup)
- ✅ Code review practices
- ⚠️ **Automated tests**: In progress (pytest suite being added)

### To Run Tests (Future)
```bash
cd backend
pytest tests/ -v --cov=app
```

---

## 📈 Performance & Scalability

### Current Bottlenecks
| Bottleneck | Impact | Mitigation |
|------------|--------|-----------|
| Docker startup | ~1-2s per submission | Reuse containers (future), or K8s init containers |
| LLM latency | ~1-3s per hint | Groq is fastest free option |
| Database connections | Limited by PostgreSQL max_connections | Connection pooling (implemented) |
| WebSocket connections | Single machine limit | Stateless backend + message queue |

### Scaling Path
1. **Current**: Single Docker host, single PostgreSQL instance
2. **Phase 1**: Database replication, connection pooling
3. **Phase 2**: Kubernetes cluster, horizontal pod autoscaling
4. **Phase 3**: Distributed submission queue (RabbitMQ/Kafka), multi-region

---

## 🚦 Getting Started with Development

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev  # Starts Vite dev server at localhost:5173 with HMR
```

### Adding a New Feature

**Example: Add a new problem type**

1. **Backend**: Update `models.py` (add field to `Problem`)
2. **Database**: Create migration (Alembic)
3. **API**: Update `routes/problems.py` endpoint
4. **Frontend**: Update `types/index.ts` and `pages/Problem.tsx`
5. **Test**: Add test case to `tests/` directory

---

## 🎓 Learning Outcomes

Building CodeLens demonstrates proficiency in:

- ✅ **Async/Concurrent Systems**: FastAPI async handlers, WebSocket, asyncio
- ✅ **Security**: Sandboxing, input validation, JWT, environment secrets
- ✅ **Real-Time Communication**: WebSocket protocol, event streaming
- ✅ **Database Design**: Relational schema, JSON columns, ORM relationships
- ✅ **Docker**: Containerization, isolation, resource limits
- ✅ **Frontend Architecture**: React hooks, Context API, component composition
- ✅ **API Design**: REST semantics, error handling, versioning
- ✅ **DevOps**: Docker Compose orchestration, local development workflows
- ✅ **LLM Integration**: Prompt engineering, grounding context, token management

---

## 🔮 Future Roadmap

### Short Term (1-2 months)
- [ ] Add pytest suite with 70%+ coverage
- [ ] Set up GitHub Actions CI/CD pipeline
- [ ] Add structured logging (Sentry integration)
- [ ] Deploy to cloud (Fly.io / Heroku)
- [ ] Add problem recommendation engine

### Medium Term (3-6 months)
- [ ] Multi-language support (Java, C++, JavaScript)
- [ ] Kubernetes deployment (Helm charts)
- [ ] Problem rating system (difficulty calibration)
- [ ] Contest mode (timed leaderboard)
- [ ] Mobile app (React Native)

### Long Term (6+ months)
- [ ] Advanced analytics dashboard
- [ ] Peer code review system
- [ ] IDE plugin (VS Code extension)
- [ ] Offline mode support
- [ ] Problem-specific test framework plugins

---

## 📝 API Response Examples

### Submit Code + Stream Results

**Request:**
```bash
curl -X POST http://localhost:8000/submissions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_id": "abc123",
    "code": "def solution(nums):\n    return nums"
  }'
```

**Response:**
```json
{
  "id": "submission-uuid-123",
  "user_id": "user-uuid",
  "problem_id": "problem-uuid",
  "code": "def solution(nums):\n    return nums",
  "status": "pending",
  "test_results": null,
  "passed_count": 0,
  "total_count": 3,
  "created_at": "2026-06-18T10:30:00"
}
```

**WebSocket Stream:**
```json
{"index":0,"status":"passed","input":"[1,2,3]","expected":"6","actual":"6","elapsed_ms":1.2}
{"index":1,"status":"failed","input":"[]","expected":"0","actual":"None","error":null,"elapsed_ms":0.8}
{"index":2,"status":"passed","input":"[100]","expected":"100","actual":"100","elapsed_ms":1.1}
```

### Generate Hint

**Request:**
```bash
curl -X POST http://localhost:8000/submissions/submission-id/hint \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"level": 2}'
```

**Response:**
```json
{
  "id": "hint-uuid",
  "submission_id": "submission-id",
  "level": 2,
  "content": "Your loop doesn't handle the case when the array is empty. You're trying to access the first element without checking if the array exists first.",
  "was_helpful": null,
  "created_at": "2026-06-18T10:32:00"
}
```

---

## 🤝 Contributing

We welcome contributions! Please:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write tests** for new functionality
4. **Commit** with clear messages (`git commit -m 'Add: amazing feature'`)
5. **Push** to your branch (`git push origin feature/amazing-feature`)
6. **Open a Pull Request** with description

### Code Style
- Backend: PEP 8 (use `black` formatter)
- Frontend: Prettier + ESLint
- Commit: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) file for details.

---

## 📧 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/Bichu0077/CodeLens/issues)
- **Author**: [Bichu0077](https://github.com/Bichu0077)
- **Email**: [Your email here]

---

## 🙏 Acknowledgments

- **FastAPI**: Modern async web framework
- **Groq**: Fast LLM inference
- **Monaco Editor**: Professional code editing experience
- **PostgreSQL**: Reliable, feature-rich database
- **React**: Component-driven UI architecture

---

**Built with ❤️ for the coding community.**