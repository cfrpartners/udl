# Komodo reStructuredText language service.
#

from xpcom import components

import logging
from koUDLLanguageBase import KoUDLLanguage

log = logging.getLogger("koReStructuredTextLanguage")
#log.setLevel(logging.DEBUG)

def registerLanguage(registry):
    log.debug("Registering language reStructuredText")
    registry.registerLanguage(KoReStructuredTextLanguage())


class KoReStructuredTextLanguage(KoUDLLanguage):
    name = "reStructuredText"
    lexresLangName = "reStructuredText"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" % name
    _reg_clsid_ = "{6072ecd4-525e-11db-82d8-000d935d3368}"
    defaultExtension = '.rst'
    primary = 0

    lang_from_udl_family = {'CSL': name, 'TPL': name, 'M': 'HTML', 'CSS': 'CSS', 'SSL': 'Python'}
    _total_string_styles = None
    
    def getStringStyles(self):
        if self._total_string_styles is None:
            scin = components.interfaces.ISciMoz
            self._total_string_styles = [scin.SCE_UDL_CSL_DEFAULT,
                                   scin.SCE_UDL_CSL_COMMENT,
                                   scin.SCE_UDL_CSL_COMMENTBLOCK,
                                   scin.SCE_UDL_CSL_NUMBER,
                                   scin.SCE_UDL_CSL_STRING,
                                   scin.SCE_UDL_CSL_WORD,
                                   scin.SCE_UDL_CSL_IDENTIFIER,
                                   scin.SCE_UDL_CSL_OPERATOR,
                                   scin.SCE_UDL_CSL_REGEX,
                                   ] + KoUDLLanguage.getStringStyles(self)
        return self._total_string_styles
