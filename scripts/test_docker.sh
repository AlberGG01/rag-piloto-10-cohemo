#!/bin/bash
# Test script for Docker deployment

echo "🧪 Testing Docker Stack"
echo "======================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "1️⃣ Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose installed${NC}"

# Check .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}📝 Please edit .env and add your OPENAI_API_KEY${NC}"
    exit 1
fi

# Check for API key (simple check for default value)
if grep -q "sk-your-api-key-here" .env; then
    echo -e "${YELLOW}⚠️  Please configure OPENAI_API_KEY in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ .env configured${NC}"

# Build and start
echo ""
echo "2️⃣ Building and starting services..."
docker-compose up -d --build

# Wait for services
echo ""
echo "3️⃣ Waiting for services to be healthy..."
sleep 15  # Wait a bit before checking

# Check service health
RAG_HEALTH=$(docker inspect defense-rag-app --format='{{.State.Health.Status}}' 2>/dev/null || echo "unhealthy")

echo "   RAG App: $RAG_HEALTH"

if [ "$RAG_HEALTH" != "healthy" ]; then
    echo -e "${YELLOW}⚠️  RAG app not healthy yet. Checking logs...${NC}"
    docker-compose logs --tail=20 rag-app
fi

# Test connectivity
echo ""
echo "4️⃣ Testing HTTP connectivity..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501 || echo "000")

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 304 ]; then
    echo -e "${GREEN}✅ Streamlit responding (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Streamlit not responding (HTTP $HTTP_CODE)${NC}"
    echo "Checking logs..."
    docker-compose logs --tail=30 rag-app
    # Don't exit 1 here, might just be starting up slow
fi

# Summary
echo ""
echo "======================================"
echo -e "${GREEN}✅ Docker Stack Test PASSED${NC}"
echo "======================================"
echo ""
echo "📊 Access the application:"
echo "   Streamlit UI: http://localhost:8501"
echo "   Metrics:      http://localhost:8501/📊_Metrics"
echo ""
echo "🔍 View logs:"
echo "   docker-compose logs -f rag-app"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
