test-build:
	@ sudo python -m jocker.run --jockerfile examples/Jockerfile build --install

test-create:
	@ sudo python -m jocker.run create --base web --name website

test: test-build test-create

.PHONY: test test-create test-build
