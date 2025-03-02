rear-%-clean.tar.gz: rear-%.tar.gz
	set -o pipefail; gunzip -c $< | tar --delete "rear-"$*"/doc/rear-release-notes.txt" -f - | gzip -c - > $@.tmp
	mv $@.tmp $@
