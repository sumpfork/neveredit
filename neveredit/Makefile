#rules added by sumpfork (sumpfork@users.sf.net) to make mac os app and dmg
#somewhat messy - sorry
PROGRAM = neveredit
VERSION=$(shell python -c 'import sys;sys.path.insert(0,"..");import neveredit;print neveredit.__version__')
INSTALL=/usr/bin/install
RESCOMP = /Developer/Tools/Rez
IMAGE = /Volumes/neveredit
AWK = awk
DU = du
HDIUTIL = hdiutil
CP = ditto --rsrc
SOURCES = ${FILES:%.py}
CXFREEZE_HOME = /opt/cx_Freeze-3.0.1

change: ${FILES:%.py}
	cvs2cl -S --no-wrap --accum --tags --prune --ignore Changelog

upload:
	-curl -# -T neveredit-$(VERSION).tar.gz ftp://upload.sf.net/incoming/
	-curl -# -T neveredit-$(VERSION).dmg ftp://upload.sf.net/incoming/
	-curl -# -T neveredit-$(VERSION).linux_i386.tar.gz ftp://upload.sf.net/incoming/
	-curl -# -T neverscript-$(VERSION).dmg ftp://upload.sf.net/incoming/
	-curl -# -T neverscript-$(VERSION).linux_i386.tar.gz ftp://upload.sf.net/incoming/

upload-beta:
	-scp {neveredit-${VERSION}.dmg,neveredit-${VERSION}.tar.gz} sumpfork@shell.sf.net:/home/groups/o/op/openknights/htdocs/neveredit/
	-scp neveredit-${VERSION}.linux_i386.tar.gz sumpfork@shell.sf.net:/home/groups/o/op/openknights/htdocs/neveredit/
	-scp neverscript-${VERSION}.dmg sumpfork@shell.sf.net:/home/groups/o/op/openknights/htdocs/neveredit/
	-scp neverscript-${VERSION}.linux_i386.tar.gz sumpfork@shell.sf.net:/home/groups/o/op/openknights/htdocs/neveredit/

targz:
	rm -fr neveredit
	cvs -d :ext:sumpfork@cvs.sourceforge.net:/cvsroot/neveredit export -r now neveredit
	rm -f neveredit-$(VERSION).tar.gz
	tar czvf neveredit-$(VERSION).tar.gz neveredit
	rm -fr neveredit

freeze-neverscript: MAINFILE=ScriptEditor.py 
freeze-neverscript: FREEZE_OUT=neverscript
freeze-neverscript: freeze

freeze-neveredit: MAINFILE=NeverEditMainApp.py
freeze-neveredit: FREEZE_OUT=neveredit
freeze-neveredit: freeze

freeze:
	(echo "freezing " $(FREEZE_OUT))
	rm -fr build/$(FREEZE_OUT)
	mkdir -p build/$(FREEZE_OUT)
	cd ui;python $(CXFREEZE_HOME)/FreezePython.py\
	$(MAINFILE)\
	--install-dir ../build/$(FREEZE_OUT)\
	--include-path=../..\
	--include-modules=neveredit,encodings,encodings.ascii,encodings.latin_1,encodings.utf_8,PIL.TgaImagePlugin,numarray.libnumarray,numarray._ufunc,numarray._ufuncComplex64,numarray._ufuncInt16,numarray._ufuncInt8,numarray._ufuncUInt64,numarray._ufuncBool,numarray._ufuncFloat32,numarray._ufuncInt32,numarray._ufuncUInt16,numarray._ufuncUInt8,numarray._ufuncComplex32,numarray._ufuncFloat64,numarray._ufuncInt64,numarray._ufuncUInt32,numarray.dotblas\
	--init-script ConsoleSetLibPath\
	--target-name=$(FREEZE_OUT)
	cp neveredit*.jpg build/$(FREEZE_OUT)
	cp README build/$(FREEZE_OUT)
	cp COPYING build/$(FREEZE_OUT)
	cp help_nwnlexicon.zip build/$(FREEZE_OUT)
	cd build/$(FREEZE_OUT);sh ../../chrpath.sh
	cd build;tar czvf ../$(FREEZE_OUT)-$(VERSION).linux_i386.tar.gz $(FREEZE_OUT)/

install: ${FILES:%.py}
	python setup.py install

documentation: ${FILES:%.py}
	epydoc --html -n neveredit -o html -u "http://openknights.sourceforge.net/tikiwiki/tiki-index.php?page=neveredit" ./

upload-docs:
	rsync -avPz --delete html/ sumpfork@shell.sf.net:/home/groups/o/op/openknights/htdocs/neveredit/docs/

bundle: $(SOURCES)
	python setup.py py2app
#python makebundle.py $(VERSION) neveredit

neverscript: $(SOURCES)
	python makebundle.py $(VERSION) neverscript

versioned-dmg: $(PROGRAM).dmg
	mv -f $(PROGRAM).dmg $(PROGRAM)-$(VERSION).dmg

$(PROGRAM)_simple.dmg:
	@$(INSTALL) -d $(IMAGE)
	@$(INSTALL) -d $(IMAGE)/$(PROGRAM).app
	$(CP) $(PWD)/README $(IMAGE)/README
	$(CP) $(PWD)/COPYING $(IMAGE)/COPYING
	$(CP) -V $(PWD)/build/$(PROGRAM).app/ $(IMAGE)/$(PROGRAM).app/
	$(HDIUTIL) create -sectors `$(DU) -s $(IMAGE) | $(AWK) '{print 2.5*$$1}'` -volname $(PROGRAM) -fs HFS -ov $(PROGRAM)
	$(HDIUTIL) attach $@ 2>&1 | grep $(PROGRAM) | cut -d ' ' -f1 > mountloc.tmp
	$(CP) $(IMAGE)/ /Volumes/$(PROGRAM)
	$(HDIUTIL) detach `cat mountloc.tmp`
	$(RM) mountloc.tmp
	$(HDIUTIL) resize $@ -size min
	mv -f $@ $(PROGRAM).tmp.dmg
	$(HDIUTIL) convert $(PROGRAM).tmp.dmg -format UDZO -imagekey zlib-level=2 -o $@
	$(RM) $(PROGRAM).tmp.dmg

#you need an existing dmg called 'neveredit_build.dmg' for the next rules
#without this it's very hard to get the right icon positions and background image in the final dmg
#just user the _simple rule above for building a simpler dmg that doesn't require an existing source dmg
$(PROGRAM).dmg:
	rm -f $@
	$(HDIUTIL) mount neveredit_build.dmg.sparseimage
#	@$(INSTALL) -d $(IMAGE)
#	@$(INSTALL) -d $(IMAGE) $(PROGRAM).app
#	@$(INSTALL) -d $(IMAGE) .background
#	$(CP) $(PWD)/.background/neveredit_background.jpg $(IMAGE)/.background/
	$(CP) $(PWD)/README $(IMAGE)/README
	/Developer/Tools/SetFile -t 'TEXT' $(IMAGE)/README
	$(CP) $(PWD)/COPYING $(IMAGE)/COPYING
	/Developer/Tools/SetFile -t 'TEXT' $(IMAGE)/COPYING
	rm -fr $(IMAGE)/$(PROGRAM).app
	$(CP) -V $(PWD)/build/$(PROGRAM).app $(IMAGE)/$(PROGRAM).app
#	$(CP) -V $(PWD)/build/$(PROGRAM).app/Contents/Resources/NeverEditMainApp.py $(IMAGE)/$(PROGRAM).app/Contents/Resources/
#	$(CP) -V $(PWD)/build/$(PROGRAM).app/Contents/Info.plist $(IMAGE)/$(PROGRAM).app/Contents/
	$(HDIUTIL) detach `hdiutil info | grep "$(IMAGE)" | awk '{print $$1}'`
#	$(HDIUTIL) create -ov -srcfolder $(IMAGE) -format UDZO -scrub -volname "neveredit" "$@"
	$(HDIUTIL) convert -ov neveredit_build.dmg.sparseimage -format UDZO -o "$@" -imagekey zlib-level=9

