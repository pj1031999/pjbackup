INSTALL = /usr/bin/install

install: pjbackup.py
	$(INSTALL) -m 755 ./pjbackup.py /usr/local/bin
	mkdir -p /etc/pjbackup
	$(INSTALL) ./conf /etc/pjbackup

uninstall:
	rm /usr/local/bin/pjbackup
	rm /etc/pjbackup/conf
	rm /etc/pjbackup
