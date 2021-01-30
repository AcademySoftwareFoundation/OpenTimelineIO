# Makefile for Doxygen documentation
#

.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo " [config]       Your doxygen configuration file"


.PHONY: clean 
clean:
	rm -rf output/html output/latex output/xml

doc:
	@doxygen config/dox_config