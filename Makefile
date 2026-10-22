.PHONY: help install run test clean deploy logs

help:
	@echo "Swiggy Telegram Bot - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "make install    - Install dependencies"
	@echo "make run        - Run bot locally"
	@echo "make test       - Test Python syntax"
	@echo "make clean      - Clean cache and logs"
	@echo "make deploy     - Setup GitHub & Railway"
	@echo "make logs       - Show bot logs"
	@echo ""

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

run:
	@echo "🚀 Starting bot..."
	python bot.py

test:
	@echo "🧪 Testing Python syntax..."
	python -m py_compile bot.py
	@echo "✅ No syntax errors"

clean:
	@echo "🧹 Cleaning cache..."
	rm -rf __pycache__ *.pyc .pytest_cache
	rm -f bot.log config.json .env
	@echo "✅ Cleaned"

deploy:
	@echo "📤 Setting up GitHub & Railway..."
	bash setup.sh

logs:
	@if [ -f bot.log ]; then \
		tail -f bot.log; \
	else \
		echo "No log file found. Run 'make run' first."; \
	fi

venv:
	@echo "🔧 Creating virtual environment..."
	python3 -m venv venv
	@echo "✅ Activate with: source venv/bin/activate"

config:
	@echo "⚙️ Setting up configuration..."
	cp .env.example .env
	@echo "✅ Edit .env with your credentials"

check:
	@echo "✅ Checking configuration..."
	@test -f .env || (echo "❌ .env not found. Run 'make config'"; exit 1)
	@test -f requirements.txt || (echo "❌ requirements.txt not found"; exit 1)
	@test -f bot.py || (echo "❌ bot.py not found"; exit 1)
	@echo "✅ All files present"

all: install check test run
