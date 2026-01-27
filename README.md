# Website User Management System

A full-stack web application demonstrating modern best practices for API development, database management, and real-time communication. Built with FastAPI, SQLAlchemy, and PostgreSQL with a responsive HTML/CSS/JavaScript frontend.

## Overview

This project serves as a comprehensive learning platform for full-stack web development, featuring a production-ready user management system with CRUD operations, database integration, and experimental networking components for real-time communication.

## Features

### Core Functionality
- **User Management API** - Full CRUD operations for user data with FastAPI
- **Database Abstraction** - SQLAlchemy ORM for seamless database interactions
- **Multi-Database Support** - Compatible with SQLite (development) and PostgreSQL (production)
- **RESTful Endpoints** - Standards-compliant API design for easy integration
- **Interactive Dashboard** - Real-time web interface for managing users

### Advanced Features
- **WebSocket Communication** - Bidirectional real-time data exchange
- **Socket Programming** - TCP/IP socket experimentation for networking fundamentals
- **File Management** - File upload and storage capabilities
- **Authentication Ready** - Foundation for implementing authentication layers

## Architecture

### Project Structure

```
website/
├── backend/                 # FastAPI server configuration
├── frontend/               # React/JavaScript components
├── database/               # Database models and migrations
├── portfolio/              # Portfolio showcase components
├── storage-web/            # File storage management
├── main.py                 # Application entry point
├── database.py             # Database connection & session setup
├── databasemodels.py       # SQLAlchemy ORM models
├── functions.py            # Business logic & CRUD operations
├── data.py                 # Data utilities and helpers
├── index.html              # Dashboard interface
├── style.css               # Frontend styling
├── script.js               # Client-side logic
├── requirements.txt        # Python dependencies
└── package.json            # Node.js dependencies
```

### Technology Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework with automatic API documentation
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM for database abstraction
- [PostgreSQL](https://www.postgresql.org/) - Robust relational database (production)
- [SQLite](https://www.sqlite.org/) - Lightweight database (development)

**Frontend**
- HTML5 - Semantic markup
- CSS3 - Modern responsive styling
- JavaScript - Client-side interactivity
- WebSockets - Real-time communication

**DevOps & Tools**
- Python 3.x
- Node.js
- Git & GitHub

## Quick Start

### Prerequisites

Ensure you have the following installed:
- Python 3.8+
- Node.js 14+
- PostgreSQL 12+ (optional, SQLite for local development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MKarthik730/website.git
   cd website
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies** (if applicable)
   ```bash
   npm install
   ```

5. **Configure database**
   - For SQLite (default): No configuration needed, `test.db` will be created automatically
   - For PostgreSQL: Update `database.py` with your connection string

6. **Run the application**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

7. **Access the dashboard**
   Open `http://localhost:8000` in your browser to access the interactive dashboard

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI** - `http://localhost:8000/docs`
- **ReDoc** - `http://localhost:8000/redoc`

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | Retrieve all users |
| `GET` | `/users/{id}` | Get specific user |
| `POST` | `/users` | Create new user |
| `PUT` | `/users/{id}` | Update user |
| `DELETE` | `/users/{id}` | Delete user |

## Configuration

### Database Configuration

Edit `database.py` to switch between SQLite and PostgreSQL:

```python
# SQLite (development)
DATABASE_URL = "sqlite:///./test.db"

# PostgreSQL (production)
DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

### Environment Variables

Create a `.env` file for sensitive configuration:
```
DATABASE_URL=postgresql://user:password@localhost/dbname
DEBUG=True
SECRET_KEY=your-secret-key
```

## Testing

Run tests with pytest (when configured):
```bash
pytest
```

## Dependencies

### Python
- fastapi
- sqlalchemy
- psycopg2-binary (for PostgreSQL)
- uvicorn
- pydantic

See `requirements.txt` for complete list.

### JavaScript
- See `package.json` for details

## Real-Time Features

### WebSocket Server
The application includes experimental WebSocket servers for learning:
- `sockets.py` - WebSocket implementation
- `server01.py` - TCP server example
- `client.py`, `client02.py` - Client implementations

### File Management
Storage and file handling through the `/storage-web` module for file upload/download operations.

## Learning Outcomes

This project demonstrates proficiency in:
- Full-stack web development
- RESTful API design principles
- Object-relational mapping (ORM)
- Database design and optimization
- Frontend-backend integration
- Real-time communication protocols
- Professional code organization
- Production-ready project structure

## Security Considerations

- Database parameterization prevents SQL injection
- Input validation through Pydantic models
- CORS configuration for safe cross-origin requests
- Foundation for JWT authentication
- Prepared for role-based access control (RBAC)

## Future Enhancements

- [ ] JWT authentication & authorization
- [ ] User roles and permissions
- [ ] API rate limiting
- [ ] Comprehensive unit test suite
- [ ] Docker containerization
- [ ] CI/CD pipeline integration
- [ ] Advanced caching strategies
- [ ] Database migrations (Alembic)

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Author

**MKarthik730**
- GitHub: [@MKarthik730](https://github.com/MKarthik730)
- Repository: [website](https://github.com/MKarthik730/website)

## Support

For issues, questions, or suggestions, please:
- Open an [issue](https://github.com/MKarthik730/website/issues) on GitHub
- Check existing documentation and examples
- Review the FastAPI [official documentation](https://fastapi.tiangolo.com/)

## Learning Resources

- [FastAPI Official Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [RESTful API Design Best Practices](https://restfulapi.net/)

---

**Last Updated**: January 2026  
**Version**: 1.0.0  
**Status**: Active Development
