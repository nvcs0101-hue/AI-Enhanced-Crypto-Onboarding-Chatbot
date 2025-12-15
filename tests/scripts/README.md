# Script Testing with Bats

## Installation

```bash
# Install Bats
git clone https://github.com/bats-core/bats-core.git /tmp/bats
cd /tmp/bats
sudo ./install.sh /usr/local
```

## Running Tests

```bash
# Run all script tests
bats tests/scripts/

# Run specific test file
bats tests/scripts/test_backup.bats

# Verbose output
bats -t tests/scripts/
```

## Writing Tests

See existing test files for examples. Each test should:
1. Set up test environment
2. Run script in dry-run mode when possible
3. Clean up after itself
4. Test one specific behavior

## Coverage Target

🎯 Goal: 80% coverage of critical script paths
