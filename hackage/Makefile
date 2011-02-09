CURRENT = f14

all:
	./hackage-fedora.py $(CURRENT)

push:
	scp $(CURRENT) fedorapeople.org:public_html/hackage/Fedora
