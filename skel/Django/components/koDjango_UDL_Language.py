# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
# 
# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
# 
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.
# 
# The Original Code is Komodo code.
# 
# The Initial Developer of the Original Code is ActiveState Software Inc.
# Portions created by ActiveState Software Inc are Copyright (C) 2000-2007
# ActiveState Software Inc. All Rights Reserved.
# 
# Contributor(s):
#   ActiveState Software Inc
# 
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
# 
# ***** END LICENSE BLOCK *****

# Komodo Django language service.
#
# Generated by 'luddite.py' on Fri Oct 20 08:49:16 2006.
# Then put into skel/ on Fri Jul  6 14:28:38 PDT 2007

import logging
import os, sys, re
from os.path import join, dirname, exists
import tempfile
import process
import koprocessutils

from xpcom import components, nsError, ServerException
from xpcom.server import WrapObject, UnwrapObject
from koXMLLanguageBase import koHTMLLanguageBase

from koLintResult import KoLintResult
from koLintResults import koLintResults

import scimozindent

log = logging.getLogger("koDjangoLanguage")
#log.setLevel(logging.DEBUG)

def registerLanguage(registry):
    log.debug("Registering language Django")
    registry.registerLanguage(KoDjangoLanguage())


class KoDjangoLanguage(koHTMLLanguageBase):
    name = "Django"
    lexresLangName = "Django"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" % name
    _reg_clsid_ = "{5c36e354-525e-11db-82d8-000d935d3368}"
    defaultExtension = '.django.html'
    searchURL = "http://docs.djangoproject.com/en"

    lang_from_udl_family = {'CSL': 'JavaScript', 'TPL': 'Django', 'M': 'HTML', 'CSS': 'CSS'}

    sample = """{% if latest_poll_list %}
    <ul>
    {% for poll in latest_poll_list %}
        <li><a href="/polls/{{ poll.id }}/">{{ poll.question }}</a></li>
    {% endfor %}
    </ul>
{% else %}
    <p>No polls are available.</p>
{% endif %}
"""

    def __init__(self):
        koHTMLLanguageBase.__init__(self)
        self.matchingSoftChars["%"] = ("%", self.accept_matching_percent)
        self._style_info.update(
            _indent_styles = [components.interfaces.ISciMoz.SCE_UDL_TPL_OPERATOR]
            )
        self._indent_chars = u'{}'
        self._indent_open_chars = u'{'
        self._indent_close_chars = u'}'

    def accept_matching_percent(self, scimoz, pos, style_info, candidate):
        return self.softchar_accept_styled_chars(
            scimoz, pos, style_info, candidate,
            {'styled_chars' : [
                    (scimoz.SCE_UDL_TPL_OPERATOR, ord("{"))
                ]
            })

    def computeIndent(self, scimoz, indentStyle, continueComments):
        return self._computeIndent(scimoz, indentStyle, continueComments, self._style_info)

    def _computeIndent(self, scimoz, indentStyle, continueComments, style_info):
        res = self._doIndentHere(scimoz, indentStyle, continueComments, style_info)
        if res is None:
            return koHTMLLanguageBase._computeIndent(self, scimoz, indentStyle, continueComments, self._style_info)
        return res

    def _keyPressed(self, ch, scimoz, style_info):
        res = self._doKeyPressHere(ch, scimoz, style_info)
        if res is None:
            return koHTMLLanguageBase._keyPressed(self, ch, scimoz, style_info)
        return res

    _startWords = "else if ifchanged ifequal ifnotequal block filter for with spaceless"
    def _doIndentHere(self, scimoz, indentStyle, continueComments, style_info):
        # Returns either None or an indent string
        pos = scimoz.positionBefore(scimoz.currentPos)
        startPos = scimoz.currentPos
        style = scimoz.getStyleAt(pos)
        if style != scimoz.SCE_UDL_TPL_OPERATOR:
            return None
        if scimoz.getWCharAt(pos) != "}":
            return None
        pos -= 1
        style = scimoz.getStyleAt(pos)
        if style != scimoz.SCE_UDL_TPL_OPERATOR:
            return None
        if scimoz.getWCharAt(pos) != "%":
            return None
        curLineNo = scimoz.lineFromPosition(pos)
        lineStartPos = scimoz.positionFromLine(curLineNo)
        delta, numTags = self._getTagDiffDelta(scimoz, lineStartPos, startPos)
        if delta < 0 and numTags == 1 and curLineNo > 0:
            didDedent, dedentAmt = self.dedentThisLine(scimoz, curLineNo, startPos)
            if didDedent:
                return dedentAmt
            else:
                return None
        indentWidth = self._getIndentWidthForLine(scimoz, curLineNo)
        indent = scimoz.indent
        newIndentWidth = indentWidth + delta * indent
        if newIndentWidth < 0:
            newIndentWidth = 0
        return scimozindent.makeIndentFromWidth(scimoz, newIndentWidth)

    def _doKeyPressHere(self, ch, scimoz, style_info):
        # Returns either None or an indent string
        pos = scimoz.positionBefore(scimoz.currentPos)
        startPos = scimoz.currentPos
        if startPos < 5:
            return None
        style = scimoz.getStyleAt(pos)
        if style != scimoz.SCE_UDL_TPL_OPERATOR:
            return None
        if scimoz.getWCharAt(pos) != "}":
            return None
        pos -= 1
        if style != scimoz.SCE_UDL_TPL_OPERATOR:
            return None
        if scimoz.getWCharAt(pos) != "%":
            return None
        pos -= 1
        curLineNo = scimoz.lineFromPosition(pos)
        lineStartPos = scimoz.positionFromLine(curLineNo)
        delta, numTags = self._getTagDiffDelta(scimoz, lineStartPos, startPos)
        if delta < 0 and numTags == 1 and curLineNo > 0:
            didDedent, dedentAmt = self.dedentThisLine(scimoz, curLineNo, startPos)
            if didDedent:
                return dedentAmt
        return None

    def _getTagDiffDelta(self, scimoz, lineStartPos, startPos):
        data = scimoz.getStyledText(lineStartPos, startPos)
        chars = data[0::2]
        styles = [ord(x) for x in data[1::2]]
        lim = len(styles)
        delta = 0
        numTags = 0
        i = 0
        limSub1 = lim - 1
        while i < limSub1:
            if (styles[i] == scimoz.SCE_UDL_TPL_OPERATOR
                and styles[i + 1] == scimoz.SCE_UDL_TPL_OPERATOR
                and chars[i] == '{'
                and chars[i + 1] == "%"):
                j = i + 2
                while (j < lim
                       and styles[j] == scimoz.SCE_UDL_TPL_DEFAULT):
                    j += 1
                if styles[j] != scimoz.SCE_UDL_TPL_WORD:
                    i = j + 1
                    continue
                wordStart = j
                while (j < lim
                       and styles[j] == scimoz.SCE_UDL_TPL_WORD):
                    j += 1
                word = chars[wordStart:j]
                if word.startswith('end'):
                    delta -= 1
                    numTags += 1
                elif word in self._startWords:
                    delta += 1
                    numTags += 1
                i = j
            else:
                i += 1
        return delta, numTags

class KoDjangoLinter(object):
    _com_interfaces_ = [components.interfaces.koILinter]
    _reg_desc_ = "Django Template Linter"
    _reg_clsid_ = "{c30d9ea6-bb99-474d-9488-4d92dd833acb}"
    _reg_contractid_ = "@activestate.com/koLinter?language=Django;1"
    _reg_categories_ = [
        ("category-komodo-linter", 'Django'),
    ]

    def __init__(self):
        self._sysUtils = components.classes["@activestate.com/koSysUtils;1"].\
            getService(components.interfaces.koISysUtils)
        self._koDirSvc = components.classes["@activestate.com/koDirs;1"].\
            getService(components.interfaces.koIDirs)
        self._userPath = koprocessutils.getUserEnv()["PATH"].split(os.pathsep)
        self._koPythonInfoEx = components.classes["@activestate.com/koAppInfoEx?app=Python;1"].\
            getService(components.interfaces.koIAppInfoEx)
        #TODO: Observe pref changes affecting self._pythonExecutable
        self._pythonExecutable = self._koPythonInfoEx.executablePath
        if not self._pythonExecutable:
            self._pythonExecutable = koDirSvc.pythonExe
        self._djangoLinterPath = join(dirname(dirname(__file__)),
                                     "pylib",
                                     "djangoLinter.py")
        self._settingsForDirs = {}
        self._lineSplitterRE = re.compile(r'\r?\n')
        self._html_linter = components.classes["@activestate.com/koLinter?language=HTML;1"].\
                            getService(components.interfaces.koILinter)
        self._nonNewline = re.compile(r'[^\r\n]')

    def _blankMatchedText(self, m):
        return self._nonNewline.sub(" ", m.group(1))

    def _walkUpDir(self, directory):
        count = 10 # Look up at most 10 levels.
        while True:
            if exists(join(directory, "settings.py")):
                return directory
            parent = dirname(directory)
            if not parent or parent == directory:
                return None
            directory = parent
            # In case the dirname logic fails...
            count -= 1
            if count <= 0:
                return None
    
    def _getSettingsDir(self, directory):
        log.debug("cur dir: %s", directory)
        dir = self._settingsForDirs.get(directory, None)
        if dir and exists(join(dir, "settings.py")):
            log.debug("Found it in directory at %s", dir)
            return dir
        fileDir = self._walkUpDir(directory)
        log.debug("_walkUpDir(%s) -> %r", directory, fileDir)
        if fileDir:
            self._settingsForDirs[directory] = fileDir
            return fileDir
        # Try the current project
        partSvc = components.classes["@activestate.com/koPartService;1"]\
                   .getService(components.interfaces.koIPartService)
        currentProject = partSvc.currentProject
        if currentProject is None:
            return None
        projDir = self._walkUpDir(currentProject.getFile().dirName)
        if projDir:
            self._settingsForDirs[directory] = projDir
        return projDir

    _djangoMatcher = re.compile(r'''(
                     (?:\{\{.*?\}\})   # Anything in {{...}}
                    |(?:\{\%.*?\%\})   # Anything in {%...%}
                    |(?:\{\#.*?\#\})   # Anything in {#...#}
                    |(?:[^\{]+)        # Anything but a {
                    |.)''',                  # Catchall
                                re.DOTALL|re.VERBOSE)
    def _extractHTMLPart(self, text):
        parts = self._djangoMatcher.findall(text)
        if not parts:
            return text
        htmlTextParts = []
        for part in parts:
            if part.startswith("{"):
                if len(part) == 1:
                    htmlTextParts.append(part)
                else:
                    htmlTextParts.append(self._spaceOutNonNewlines(part))
            else:
                htmlTextParts.append(part)
        return "".join(htmlTextParts)
    
    _nonNewlineMatcher = re.compile(r'[^\r\n]')
    def _spaceOutNonNewlines(self, markup):
        return self._nonNewlineMatcher.sub(' ', markup)

    def lint(self, request):
        return self._html_linter.lint(request)

    def lint_with_text(self, request, text):
        cwd = request.cwd
        settingsDir = self._getSettingsDir(cwd)
        if settingsDir:
            # Save the current buffer to a temporary file.
            tmpFileName = tempfile.mktemp()
            fout = open(tmpFileName, 'wb')
            try:
                fout.write(text)
                fout.close()
            
                results = koLintResults()
                argv = [self._pythonExecutable, self._djangoLinterPath,
                        tmpFileName, settingsDir]
                env = koprocessutils.getUserEnv()
                p = process.ProcessOpen(argv, cwd=cwd, env=env, stdin=None)
                output, error = p.communicate()
                #log.debug("Django output: output:[%s], error:[%s]", output, error)
                retval = p.returncode
            finally:
                os.unlink(tmpFileName)
            if retval == 1:
                if error:
                    results.addResult(self._buildResult(text, error))
                else:
                    results.addResult(self._buildResult(text, "Unexpected error"))
        else:
            result = KoLintResult()
            result.lineStart = 1
            result.lineEnd = 1
            result.columnStart = 1
            result.columnEnd = 1 + len(text.splitlines(1)[0])
            result.description = "Can't find settings.py for this Django file"
            result.encodedDescription = result.description
            result.severity = result.SEV_ERROR
            results = koLintResults()
            results.addResult(result)
        return results
            
    _simple_matchers = {
        "Empty block tag": r"\{\%\s*\%\}",
        "Empty variable tag":  r"\{\{\s*\}\}",
    }
    _contextual_matchers = {
        r"Invalid block tag:\s*'(.*?)'"               : r"\{\%%\s*(%s).*?\%%\}",
        r"Invalid filter:\s+'(.*?)'"                  : r"\|(%s)",
        r"(\S+) requires \d+ arguments?, \d+ provided" : r"\{\{\s*(.*?\|%s)",
        r"Variables and attributes may not begin with underscores: '(.*?)'"
                                                      : r"\{\{\s*(%s)",
        r"<ExtendsNode: extends \"(.*?)\"> must be the first tag in the template"
                    : r"""(\{%%\s*extends\s*["']%s["'])""",
    }
    _compiled_ptns = {}

    def _do_simple_matcher(self, ptn, text, lintResult):
        if not self._compiled_ptns.has_key(ptn):
            self._compiled_ptns[ptn] = re.compile(ptn)
        regex = self._compiled_ptns[ptn]
        m = regex.search(text)
        if not m:
            return False
        endPos = m.end()
        lines = self._lineSplitterRE.split(text[:endPos])
        lastLine = lines[-1]
        lintResult.lineStart = lintResult.lineEnd = len(lines)
        m = regex.search(lastLine)
        lintResult.columnStart = m.start() + 1
        lintResult.columnEnd = m.end() + 1
        return True

    def _do_contextual_matcher(self, ptnTemplate, arg, text, lintResult):
        ptn = ptnTemplate % (re.escape(arg),)
        if not self._compiled_ptns.has_key(ptn):
            self._compiled_ptns[ptn] = re.compile(ptn)
        regex = self._compiled_ptns[ptn]
        m = regex.search(text)
        if not m:
            return False
        endPos = m.end()
        lines = text[:endPos].splitlines()
        lastLine = lines[-1]
        lintResult.lineStart = lintResult.lineEnd = len(lines)
        m = regex.search(lastLine)
        lintResult.columnStart = m.span(1)[0] + 1
        lintResult.columnEnd = m.span(1)[1] + 1
        return True
        
    def _test_for_duplicate_extends(self, message, text, lintResult):
        # Special case: find the second occurrence, and underline it
        if "'extends' cannot appear more than once in the same template" not in message:
            return
        ptn = r"\{\%\s*extends\b.*?\%\}.*?(\{\%\s*extends\b)"
        if not self._compiled_ptns.has_key(ptn):
            self._compiled_ptns[ptn] = re.compile(ptn, re.DOTALL)
        m = self._compiled_ptns[ptn].search(text)
        if not m:
            return
        span = m.span(1)
        before_lines = text[:span[0]].splitlines()
        num_before_lines = len(before_lines)
        lines = text.splitlines()
        if len(before_lines[-1]) < len(lines[num_before_lines - 1]):
            #log.debug("Second extend starts in the middle of a line")
            lintResult.lineStart = lintResult.lineEnd = num_before_lines
            lintResult.columnStart = len(before_lines[-1]) + 1
        else:
            #log.debug("Second extend starts at the start of a line")
            lintResult.lineStart = lintResult.lineEnd = num_before_lines + 1
            lintResult.columnStart = 1
        lintResult.columnEnd = lintResult.columnStart + span[1] - span[0]
        return lintResult
                
    def _buildResult(self, text, message):
        inputLines = text.splitlines()
        r = KoLintResult()
        r.severity = r.SEV_ERROR
        r.description = message
        m = re.compile(r'TemplateSyntaxError:\s*(.*)\n').match(message)
        if m:
            message = m.group(1)
            for errorType in self._simple_matchers:
                if errorType in message:
                    if self._do_simple_matcher(self._simple_matchers[errorType],
                                               text, r):
                        return r
            for raw_ptn in self._contextual_matchers:
                if not self._compiled_ptns.has_key(raw_ptn):
                    self._compiled_ptns[raw_ptn] = re.compile(raw_ptn)
                ptn = self._compiled_ptns[raw_ptn]
                m = ptn.search(message)
                if m:
                    if self._do_contextual_matcher(self._contextual_matchers[raw_ptn], m.group(1), text, r):
                        return r
            if self._test_for_duplicate_extends(message, text, r):
                return r
                    
            # Special-case contextual pattern has two parts
            m = re.compile(r"Could not parse the remainder: '(.*?)' from '(.*?)'").search(message)
            if m:
                part2 = m.group(1)
                part1 = m.group(2)[:-1 * len(part2)]
                ptn = r'%s(%%s)' %  (re.escape(part1),)
                res = self._do_contextual_matcher(ptn, part2, text, r)
                if res:
                    return r
        # Let the Unclosed Block Tag message fall through, and highlight
        # last line, since we don't know which open-tag it's referring to
        # Underline the last line for all other unrecognized syntax errors.

        r.columnStart = 1
        problemLineIdx = len(inputLines) - 1
        while problemLineIdx >= 0 and not inputLines[problemLineIdx].strip():
            problemLineIdx -= 1
        if problemLineIdx == -1:
            r.lineStart = r.lineEnd = 1
            r.columnEnd = 1
        else:
            r.lineStart = r.lineEnd = problemLineIdx + 1
            r.columnEnd = len(inputLines[problemLineIdx])
        return r
