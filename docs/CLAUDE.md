# CLAUDE.md - Documentation Directory

## Overview
This directory contains all project documentation, design files, and architectural decisions for the Novel Task Manager application.

## Directory Structure
```
docs/
├── database_design.md     # Database schema and relationships
├── api_documentation.md   # API endpoints and usage (if created)
├── architecture.md        # System architecture overview (if created)
├── deployment.md         # Deployment instructions (if created)
└── user_guide.md        # User manual (if created)
```

## Key Documents

### database_design.md
Contains the complete database schema design including:
- Table structures and relationships
- Field definitions and constraints
- Indexes and performance considerations
- Entity relationship diagrams
- Migration strategies

## Documentation Standards

### Format Guidelines
- Use Markdown for all documentation
- Include table of contents for documents > 3 pages
- Use code blocks with syntax highlighting
- Include diagrams where applicable
- Version and date all documents

### Code Examples
Always include working examples:
```python
# Example API call
response = requests.post(
    "http://localhost:8000/api/v1/tasks/upload",
    files={"file": open("novel.txt", "rb")}
)
```

### Diagram Tools
Recommended tools for creating diagrams:
- Mermaid for flowcharts and sequence diagrams
- Draw.io for architecture diagrams
- PlantUML for UML diagrams

## Document Templates

### API Documentation Template
```markdown
## Endpoint Name
**URL**: `/api/v1/endpoint`
**Method**: `POST`
**Auth Required**: Yes/No

### Request
\```json
{
  "field": "value"
}
\```

### Response
\```json
{
  "status": "success",
  "data": {}
}
\```

### Example
\```bash
curl -X POST http://localhost:8000/api/v1/endpoint
\```
```

### Feature Documentation Template
```markdown
## Feature Name

### Overview
Brief description of the feature

### User Stories
- As a user, I want to...
- As an admin, I want to...

### Technical Implementation
- Components involved
- Data flow
- Dependencies

### Testing
- Unit tests
- Integration tests
- User acceptance criteria
```

## Documentation Maintenance

### Review Schedule
- Technical docs: Review on each major update
- User docs: Review monthly
- API docs: Auto-generate when possible

### Version Control
- Track all changes in git
- Use semantic versioning for releases
- Maintain changelog

## Quick Reference

### Common Tasks
1. **Update database schema**
   - Edit database_design.md
   - Update backend models
   - Create migration if needed

2. **Document new API endpoint**
   - Add to API documentation
   - Include request/response examples
   - Update Postman collection

3. **Add architecture decision**
   - Create ADR (Architecture Decision Record)
   - Include context, decision, consequences
   - Link from main architecture doc

## Tools & Resources

### Documentation Tools
- **Markdown Preview**: VS Code extensions
- **API Testing**: Postman, Insomnia
- **Diagrams**: Mermaid, Draw.io
- **Screenshots**: Built-in OS tools

### Style Guides
- Follow Python docstring conventions
- Use JSDoc for TypeScript/JavaScript
- Keep language simple and clear
- Include examples whenever possible

## Contributing to Documentation

### Process
1. Identify documentation gap
2. Create/update document
3. Review with team
4. Commit with descriptive message
5. Update this CLAUDE.md if structure changes

### Best Practices
- Write for your future self
- Assume no prior knowledge
- Test all code examples
- Keep documentation close to code
- Update docs with code changes

## Documentation Gaps to Address
- [ ] Deployment guide for production
- [ ] Performance tuning guide
- [ ] Security best practices
- [ ] Troubleshooting guide
- [ ] API client examples
- [ ] WebSocket client implementation guide
- [ ] Monitoring and logging setup
- [ ] Backup and recovery procedures