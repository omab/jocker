test-build-flavour:
	@ sudo python -m jocker.run build --jockerfile examples/Jockerfile --install

test-create-jail:
	@ sudo python -m jocker.run create --base web --name website --net 're0|192.168.1.52'

test-run-jail:
	@ sudo python -m jocker.run run --name website

test-run-shell:
	@ sudo python -m jocker.run run --name website --command /bin/sh

test: test-build-flavour test-create-jail

.PHONY: test test-create-jail test-build-flavour
