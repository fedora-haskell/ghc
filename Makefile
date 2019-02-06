COPR_REPO = ghc-8.6.1

TARBALL = ghc-$(VERSION)-src.tar.xz

include ../common/common.mk

CONTAINER_DIST = rawhide
CONTAINER = "fedora:$(CONTAINER_DIST)"
COPR_URL = https://copr-be.cloud.fedoraproject.org/results/petersen/$(COPR_REPO)/fedora-$(CONTAINER_DIST)-x86_64/

test:
	podman pull $(CONTAINER)
	podman run -t --rm $(CONTAINER) dnf install --assumeno --repofrompath copr-petersen-$(COPR_REPO),$(COPR_URL) ghc-8.6.1

container:
	podman pull $(CONTAINER)
	podman create -it --name $(COPR_REPO) $(CONTAINER) bash
	podman start $(COPR_REPO)
	podman exec -t $(COPR_REPO) dnf --assumeyes install dnf-plugins-core
	podman exec -t $(COPR_REPO) dnf --assumeyes copr enable petersen/$(COPR_REPO)
	podman exec -t $(COPR_REPO) dnf install --assumeyes ghc
	podman stop $(COPR_REPO)
