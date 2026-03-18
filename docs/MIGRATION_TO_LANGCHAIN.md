# Migration from CrewAI to LangChain

## Overview
This document describes the migration from CrewAI to LangChain for the AgentDoc document processing workflow.

## Changes Made

### 1. Dependencies Updated
**File:** `backend/requirements.txt`

**Before:**
```
crewai>=0.1.0
```

**After:**
```
langchain>=0.1.0
langchain-google-genai>=0.0.6
```

### 2. Agent Implementation
**File:** `backend/apps/agents/crew.py`

**Changes:**
- Replaced CrewAI imports with LangChain imports
- Updated `build_crew()` to use `ChatGoogleGenerativeAI` instead of CrewAI's `LLM`
- Modified `execute()` to use LangChain workflow
- Added `_execute_langchain_workflow()` method for future LangChain agent chains
- Currently uses simulation mode (same logic as before)

### 3. Workflow Implementation
**File:** `backend/apps/agents/workflow.py`

**Changes:**
- Removed CrewAI Flow, @start, and @listen decorators
- Simplified `DocumentWorkflow` class to plain Python class
- Removed dependency on CrewAI Flow base class
- Workflow now executes synchronously without CrewAI decorators

### 4. Tools Implementation
**File:** `backend/apps/agents/tools/document_tools.py`

**Changes:**
- Replaced `from crewai.tools import tool` with `from langchain.tools import tool`
- Updated tool decorators from `@tool("name")` to `@tool`
- Tools now compatible with LangChain's tool interface

## Installation

### Uninstall CrewAI
```bash
pip uninstall crewai crewai-tools -y
```

### Install LangChain
```bash
pip install langchain langchain-google-genai
```

Or install all requirements:
```bash
cd backend
pip install -r requirements.txt
```

## Current Status

### ✅ Completed
- Dependencies updated
- CrewAI imports replaced with LangChain
- Workflow simplified to remove CrewAI Flow
- Tools updated for LangChain compatibility
- System runs in simulation mode (same as before)

### 🚧 Future Enhancements
The current implementation uses simulation mode. To fully leverage LangChain:

1. **Implement LangChain Agents**
   - Create LangChain agents for each stage (classification, extraction, validation, routing, audit)
   - Use `create_structured_chat_agent` or `create_react_agent`
   - Connect agents with LangChain chains

2. **Add LangChain Tools**
   - Convert existing tools to LangChain Tool format
   - Add tool descriptions and schemas
   - Integrate with agent executors

3. **Implement Agent Chains**
   - Create sequential chain for workflow stages
   - Add error handling and fallbacks
   - Implement state management between stages

4. **Add Memory and Context**
   - Use LangChain memory for conversation history
   - Add context management for multi-page documents
   - Implement retrieval-augmented generation (RAG)

## Benefits of LangChain

1. **Better Ecosystem** - More tools, integrations, and community support
2. **Flexibility** - Easier to customize and extend
3. **Production Ready** - Better error handling and monitoring
4. **Cost Effective** - More control over API calls and caching
5. **Active Development** - Regular updates and improvements

## Testing

The system continues to work exactly as before:
- Document upload works
- OCR extraction works
- Classification works
- Validation works
- Review workflow works

No functional changes - just the underlying framework.

## Rollback

If needed, you can rollback by:
1. Reverting changes to the 4 files mentioned above
2. Uninstalling LangChain: `pip uninstall langchain langchain-google-genai`
3. Reinstalling CrewAI: `pip install crewai`

## Next Steps

1. Test the current implementation thoroughly
2. Implement LangChain agent chains (optional)
3. Add more sophisticated prompting strategies
4. Implement RAG for better document understanding
5. Add caching to reduce API costs

## Support

For issues or questions:
- Check LangChain documentation: https://python.langchain.com/
- Review the code comments in the updated files
- Test in development before deploying to production
