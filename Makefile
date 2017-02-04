INSTALL = /usr/bin/install

install: pjbackup.py
	$(INSTALL) 755 ./pjbackup.py /usr/local/bin/pjbackup
	mkdir -p /etc/pjbackup
	$(INSTALL) ./conf /etc/pjbackup/conf
