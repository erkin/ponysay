#!/usr/bin/env python3
# -*- coding: utf-8 -*-


###############################################################################################
## Shell auto-completion script generator https://www.github.com/maandree/auto-auto-complete ##
## Used by build system to make completions for all supported shells.                        ##
###############################################################################################


'''
auto-auto-complete – Autogenerate shell auto-completion scripts

Copyright © 2012  Mattias Andrée (maandree@kth.se)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys


'''
Hack to enforce UTF-8 in output (in the future, if you see anypony not using utf-8 in
programs by default, report them to Princess Celestia so she can banish them to the moon)

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def print(text = '', end = '\n'):
    sys.stdout.buffer.write((str(text) + end).encode('utf-8'))

'''
stderr equivalent to print()

@param  text:str  The text to print (empty string is default)
@param  end:str   The appendix to the text to print (line breaking is default)
'''
def printerr(text = '', end = '\n'):
    sys.stderr.buffer.write((str(text) + end).encode('utf-8'))




'''
Bracket tree parser
'''
class Parser:
    '''
    Parse a code and return a tree
    
    @param   code:str      The code to parse
    @return  :list<↑|str>  The root node in the tree
    '''
    @staticmethod
    def parse(code):
        stack = []
        stackptr = -1
        
        comment = False
        escape = False
        quote = None
        buf = None
        
        for charindex in range(0, len(code)):
            c = code[charindex]
            if comment:
                if c in '\n\r\f':
                    comment = False
            elif escape:
                escape = False
                if   c == 'a':  buf += '\a'
                elif c == 'b':  buf += chr(8)
                elif c == 'e':  buf += '\033'
                elif c == 'f':  buf += '\f'
                elif c == 'n':  buf += '\n'
                elif c == 'r':  buf += '\r'
                elif c == 't':  buf += '\t'
                elif c == 'v':  buf += chr(11)
                elif c == '0':  buf += '\0'
                else:
                    buf += c
            elif c == quote:
                quote = None
            elif (c in ';#') and (quote is None):
                if buf is not None:
                    stack[stackptr].append(buf)
                    buf = None
                comment = True
            elif (c == '(') and (quote is None):
                if buf is not None:
                    stack[stackptr].append(buf)
                    buf = None
                stackptr += 1
                if stackptr == len(stack):
                    stack.append([])
                else:
                    stack[stackptr] = []
            elif (c == ')') and (quote is None):
                if buf is not None:
                    stack[stackptr].append(buf)
                    buf = None
                if stackptr == 0:
                    return stack[0]
                stackptr -= 1
                stack[stackptr].append(stack[stackptr + 1])
            elif (c in ' \t\n\r\f') and (quote is None):
                if buf is not None:
                    stack[stackptr].append(buf)
                    buf = None
            else:
                if buf is None:
                    buf = ''
                if c == '\\':
                    escape = True
                elif (c in '\'\"') and (quote is None):
                    quote = c
                else:
                    buf += c
        
        raise Exception('premature end of file')
    
    
    '''
    Simplifies a tree
    
    @param  tree:list<↑|str>  The tree
    '''
    @staticmethod
    def simplify(tree):
        program = tree[0]
        stack = [tree]
        while len(stack) > 0:
            node = stack.pop()
            new = []
            edited = False
            for item in node:
                if isinstance(item, list):
                    if item[0] == 'multiple':
                        master = item[1]
                        for slave in item[2:]:
                            new.append([master] + slave)
                        edited = True
                    elif item[0] == 'case':
                        for alt in item[1:]:
                            if alt[0] == program:
                                new.append(alt[1])
                                break
                        edited = True
                    else:
                        new.append(item)
                else:
                    new.append(item)
            if edited:
                node[:] = new
            for item in node:
                if isinstance(item, list):
                    stack.append(item)



'''
Completion script generator for GNU Bash
'''
class GeneratorBASH:
    '''
    Constructor
    
    @param  program:str                              The command to generate completion for
    @param  unargumented:list<dict<str, list<str>>>  Specification of unargumented options
    @param  argumented:list<dict<str, list<str>>>    Specification of argumented options
    @param  variadic:list<dict<str, list<str>>>      Specification of variadic options
    @param  suggestion:list<list<↑|str>>             Specification of argument suggestions
    @param  default:dict<str, list<str>>?            Specification for optionless arguments
    '''
    def __init__(self, program, unargumented, argumented, variadic, suggestion, default):
        self.program      = program
        self.unargumented = unargumented
        self.argumented   = argumented
        self.variadic     = variadic
        self.suggestion   = suggestion
        self.default      = default
    
    
    '''
    Gets the argument suggesters for each option
    
    @return  :dist<str, str>  Map from option to suggester
    '''
    def __getSuggesters(self):
        suggesters = {}
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if 'suggest' in item:
                    suggester = item['suggest']
                    for option in item['options']:
                        suggesters[option] = suggester[0]
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if ('suggest' not in item) and ('bind' in item):
                    bind = item['bind'][0]
                    if bind in suggesters:
                        suggester = suggesters[bind]
                        for option in item['options']:
                            suggesters[option] = suggester
        
        return suggesters
    
    
    '''
    Returns the generated code
    
    @return  :str  The generated code
    '''
    def get(self):
        buf = '# bash completion for %s         -*- shell-script -*-\n\n' % self.program
        buf += '_%s()\n{\n' % self.program
        buf += '    local cur prev words cword\n'
        buf += '    _init_completion -n = || return\n\n'
        
        def verb(text):
            temp = text
            for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-+=/@:\'':
                temp = temp.replace(char, '')
            if len(temp) == 0:
                return text
            return '\'' + text.replace('\'', '\'\\\'\'') + '\''
        
        def makeexec(functionType, function):
            if functionType in ('exec', 'pipe', 'fullpipe', 'cat', 'and', 'or'):
                elems = [(' %s ' % makeexec(item[0], item[1:]) if isinstance(item, list) else verb(item)) for item in function]
                if functionType == 'exec':
                    return ' $( %s ) ' % (' '.join(elems))
                if functionType == 'pipe':
                    return ' ( %s ) ' % (' | '.join(elems))
                if functionType == 'fullpipe':
                    return ' ( %s ) ' % (' |% '.join(elems))
                if functionType == 'cat':
                    return ' ( %s ) ' % (' ; '.join(elems))
                if functionType == 'and':
                    return ' ( %s ) ' % (' && '.join(elems))
                if functionType == 'or':
                    return ' ( %s ) ' % (' || '.join(elems))
            if functionType in ('params', 'verbatim'):
                return ' '.join([verb(item) for item in function])
            return ' '.join([verb(functionType)] + [verb(item) for item in function])
        
        def makesuggestion(suggester):
            suggestion = '';
            for function in suggester:
                functionType = function[0]
                function = function[1:]
                if functionType == 'verbatim':
                    suggestion += ' %s' % (' '.join([verb(item) for item in function]))
                elif functionType == 'ls':
                    filter = ''
                    if len(function) > 1:
                        filter = ' | grep -v \\/%s\\$ | grep %s\\$' % (function[1], function[1])
                    suggestion += ' $(ls -1 --color=no %s%s)' % (function[0], filter)
                elif functionType in ('exec', 'pipe', 'fullpipe', 'cat', 'and', 'or'):
                    suggestion += (' %s' if functionType == 'exec' else ' $(%s)') % makeexec(functionType, function)
                elif functionType == 'calc':
                    expression = []
                    for item in function:
                        if isinstance(item, list):
                            expression.append(('%s' if item[0] == 'exec' else '$(%s)') % makeexec(item[0], item[1:]))
                        else:
                            expression.append(verb(item))
                    suggestion += ' $(( %s ))' % (' '.join(expression))
            return '"' + suggestion + '"'
        
        suggesters = self.__getSuggesters()
        suggestFunctions = {}
        for function in self.suggestion:
            suggestFunctions[function[0]] = function[1:]
        
        options = []
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if 'complete' in item:
                    options += item['complete']
        buf += '    options="%s "' % (' '.join(options))
        if self.default is not None:
            defSuggest = self.default['suggest'][0]
            if defSuggest is not None:
                buf += '%s' % makesuggestion(suggestFunctions[defSuggest])
        buf += '\n'
        buf += '    COMPREPLY=( $( compgen -W "$options" -- "$cur" ) )\n\n'
        
        indenticals = {}
        for option in suggesters:
            suggester = suggestFunctions[suggesters[option]]
            _suggester = str(suggester)
            if _suggester not in indenticals:
                indenticals[_suggester] = (suggester, [option])
            else:
                indenticals[_suggester][1].append(option)
        
        index = 0
        for _suggester in indenticals:
            (suggester, options) = indenticals[_suggester]
            conds = []
            for option in options:
                conds.append('[ $prev = "%s" ]' % option)
            buf += '    %s %s; then\n' % ('if' if index == 0 else 'elif', ' || '.join(conds))
            suggestion = makesuggestion(suggester);
            if len(suggestion) > 0:
                buf += '        suggestions=%s\n' % suggestion
                buf += '        COMPREPLY=( $( compgen -W "$suggestions" -- "$cur" ) )\n'
            index += 1
        
        if index > 0:
            buf += '    fi\n'
        
        buf += '}\n\ncomplete -o default -F _%s %s\n\n' % (self.program, self.program)
        return buf



'''
Completion script generator for fish
'''
class GeneratorFISH:
    '''
    Constructor
    
    @param  program:str                              The command to generate completion for
    @param  unargumented:list<dict<str, list<str>>>  Specification of unargumented options
    @param  argumented:list<dict<str, list<str>>>    Specification of argumented options
    @param  variadic:list<dict<str, list<str>>>      Specification of variadic options
    @param  suggestion:list<list<↑|str>>             Specification of argument suggestions
    @param  default:dict<str, list<str>>?            Specification for optionless arguments
    '''
    def __init__(self, program, unargumented, argumented, variadic, suggestion, default):
        self.program      = program
        self.unargumented = unargumented
        self.argumented   = argumented
        self.variadic     = variadic
        self.suggestion   = suggestion
        self.default      = default
    
    
    '''
    Gets the argument suggesters for each option
    
    @return  :dist<str, str>  Map from option to suggester
    '''
    def __getSuggesters(self):
        suggesters = {}
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if 'suggest' in item:
                    suggester = item['suggest']
                    for option in item['options']:
                        suggesters[option] = suggester[0]
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if ('suggest' not in item) and ('bind' in item):
                    bind = item['bind'][0]
                    if bind in suggesters:
                        suggester = suggesters[bind]
                        for option in item['options']:
                            suggesters[option] = suggester
        
        return suggesters
    
    
    '''
    Gets the file pattern for each option
    
    @return  :dist<str, list<str>>  Map from option to file pattern
    '''
    def __getFiles(self):
        files = {}
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if 'files' in item:
                    _files = item['files']
                    for option in item['options']:
                        files[option] = _files
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if ('files' not in item) and ('bind' in item):
                    bind = item['bind'][0]
                    if bind in files:
                        _files = files[bind]
                        for option in item['options']:
                            files[option] = _files
        
        return files
    
    
    '''
    Returns the generated code
    
    @return  :str  The generated code
    '''
    def get(self):
        buf = '# fish completion for %s         -*- shell-script -*-\n\n' % self.program
        
        files = self.__getFiles()
        
        suggesters = self.__getSuggesters()
        suggestFunctions = {}
        for function in self.suggestion:
            suggestFunctions[function[0]] = function[1:]
        
        def verb(text):
            temp = text
            for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-+=/@:\'':
                temp = temp.replace(char, '')
            if len(temp) == 0:
                return text
            return '\'' + text.replace('\'', '\'\\\'\'') + '\''
        
        def makeexec(functionType, function):
            if functionType in ('exec', 'pipe', 'fullpipe', 'cat', 'and', 'or'):
                elems = [(' %s ' % makeexec(item[0], item[1:]) if isinstance(item, list) else verb(item)) for item in function]
                if functionType == 'exec':
                    return ' ( %s ) ' % (' '.join(elems))
                if functionType == 'pipe':
                    return ' ( %s ) ' % (' | '.join(elems))
                if functionType == 'fullpipe':
                    return ' ( %s ) ' % (' |% '.join(elems))
                if functionType == 'cat':
                    return ' ( %s ) ' % (' ; '.join(elems))
                if functionType == 'and':
                    return ' ( %s ) ' % (' && '.join(elems))
                if functionType == 'or':
                    return ' ( %s ) ' % (' || '.join(elems))
            if functionType in ('params', 'verbatim'):
                return ' '.join([verb(item) for item in function])
            return ' '.join([verb(functionType)] + [verb(item) for item in function])
        
        index = 0
        for name in suggestFunctions:
            suggestion = '';
            for function in suggestFunctions[name]:
                functionType = function[0]
                function = function[1:]
                if functionType == 'verbatim':
                    suggestion += ' %s' % (' '.join([verb(item) for item in function]))
                elif functionType == 'ls':
                    filter = ''
                    if len(function) > 1:
                        filter = ' | grep -v \\/%s\\$ | grep %s\\$' % (function[1], function[1])
                    suggestion += ' (ls -1 --color=no %s%s)' % (function[0], filter)
                elif functionType in ('exec', 'pipe', 'fullpipe', 'cat', 'and', 'or'):
                    suggestion += (' %s' if functionType == 'exec' else ' $(%s)') % makeexec(functionType, function)
                #elif functionType == 'calc':
                #    expression = []
                #    for item in function:
                #        if isinstance(item, list):
                #            expression.append(('%s' if item[0] == 'exec' else '$(%s)') % makeexec(item[0], item[1:]))
                #        else:
                #            expression.append(verb(item))
                #    suggestion += ' $(( %s ))' % (' '.join(expression))
            if len(suggestion) > 0:
                suggestFunctions[name] = '"' + suggestion + '"'
        
        if self.default is not None:
            item = self.default
            buf += 'complete --command %s' % self.program
            if 'desc' in self.default:
                buf += ' --description %s' % verb(' '.join(item['desc']))
            defFiles = self.default['files']
            defSuggest = self.default['suggest'][0]
            if defFiles is not None:
                if (len(defFiles) == 1) and ('-0' in defFiles):
                    buf += ' --no-files'
            if defSuggest is not None:
                buf += ' --arguments %s' % suggestFunctions[defSuggest]
            buf += '\n'
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                options = item['options']
                shortopt = []
                longopt = []
                for opt in options:
                    if opt.startswith('--'):
                        if ('complete' in item) and (opt in item['complete']):
                            longopt.append(opt)
                    elif opt.startswith('-') and (len(opt) == 2):
                        shortopt.append(opt)
                options = shortopt + longopt
                if len(longopt) == 0:
                    continue
                buf += 'complete --command %s' % self.program
                if 'desc' in item:
                    buf += ' --description %s' % verb(' '.join(item['desc']))
                if options[0] in files:
                    if (len(files[options[0]]) == 1) and ('-0' in files[options[0]][0]):
                        buf += ' --no-files'
                if options[0] in suggesters:
                    buf += ' --arguments %s' % suggestFunctions[suggesters[options[0]]]
                if len(shortopt) > 0: buf += ' --short-option %s' % shortopt[0][1:]
                if len( longopt) > 0: buf +=  ' --long-option %s' %  longopt[0][2:]
                buf += '\n'
        
        return buf



'''
Completion script generator for zsh
'''
class GeneratorZSH:
    '''
    Constructor
    
    @param  program:str                              The command to generate completion for
    @param  unargumented:list<dict<str, list<str>>>  Specification of unargumented options
    @param  argumented:list<dict<str, list<str>>>    Specification of argumented options
    @param  variadic:list<dict<str, list<str>>>      Specification of variadic options
    @param  suggestion:list<list<↑|str>>             Specification of argument suggestions
    @param  default:dict<str, list<str>>?            Specification for optionless arguments
    '''
    def __init__(self, program, unargumented, argumented, variadic, suggestion, default):
        self.program      = program
        self.unargumented = unargumented
        self.argumented   = argumented
        self.variadic     = variadic
        self.suggestion   = suggestion
        self.default      = default
    
    
    '''
    Gets the argument suggesters for each option
    
    @return  :dist<str, str>  Map from option to suggester
    '''
    def __getSuggesters(self):
        suggesters = {}
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if 'suggest' in item:
                    suggester = item['suggest']
                    for option in item['options']:
                        suggesters[option] = suggester[0]
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if ('suggest' not in item) and ('bind' in item):
                    bind = item['bind'][0]
                    if bind in suggesters:
                        suggester = suggesters[bind]
                        for option in item['options']:
                            suggesters[option] = suggester
        
        return suggesters
    
    
    '''
    Gets the file pattern for each option
    
    @return  :dist<str, list<str>>  Map from option to file pattern
    '''
    def __getFiles(self):
        files = {}
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if 'files' in item:
                    _files = item['files']
                    for option in item['options']:
                        files[option] = _files
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                if ('files' not in item) and ('bind' in item):
                    bind = item['bind'][0]
                    if bind in files:
                        _files = files[bind]
                        for option in item['options']:
                            files[option] = _files
        
        return files
    
    
    '''
    Returns the generated code
    
    @return  :str  The generated code
    '''
    def get(self):
        buf = '# zsh completion for %s         -*- shell-script -*-\n\n' % self.program
        
        files = self.__getFiles()
        
        suggesters = self.__getSuggesters()
        suggestFunctions = {}
        for function in self.suggestion:
            suggestFunctions[function[0]] = function[1:]
        
        def verb(text):
            temp = text
            for char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-+=/@:\'':
                temp = temp.replace(char, '')
            if len(temp) == 0:
                return text
            return '\'' + text.replace('\'', '\'\\\'\'') + '\''
        
        def makeexec(functionType, function):
            if functionType in ('exec', 'pipe', 'fullpipe', 'cat', 'and', 'or'):
                elems = [(' %s ' % makeexec(item[0], item[1:]) if isinstance(item, list) else verb(item)) for item in function]
                if functionType == 'exec':
                    return ' $( %s ) ' % (' '.join(elems))
                if functionType == 'pipe':
                    return ' ( %s ) ' % (' | '.join(elems))
                if functionType == 'fullpipe':
                    return ' ( %s ) ' % (' |% '.join(elems))
                if functionType == 'cat':
                    return ' ( %s ) ' % (' ; '.join(elems))
                if functionType == 'and':
                    return ' ( %s ) ' % (' && '.join(elems))
                if functionType == 'or':
                    return ' ( %s ) ' % (' || '.join(elems))
            if functionType in ('params', 'verbatim'):
                return ' '.join([verb(item) for item in function])
            return ' '.join([verb(functionType)] + [verb(item) for item in function])
        
        index = 0
        for name in suggestFunctions:
            suggestion = '';
            for function in suggestFunctions[name]:
                functionType = function[0]
                function = function[1:]
                if functionType == 'verbatim':
                    suggestion += ' %s ' % (' '.join([verb(item) for item in function]))
                elif functionType == 'ls':
                    filter = ''
                    if len(function) > 1:
                        filter = ' | grep -v \\/%s\\$ | grep %s\\$' % (function[1], function[1])
                    suggestion += ' $(ls -1 --color=no %s%s) ' % (function[0], filter)
                elif functionType in ('exec', 'pipe', 'fullpipe', 'cat', 'and', 'or'):
                    suggestion += ('%s' if functionType == 'exec' else '$(%s)') % makeexec(functionType, function)
                elif functionType == 'calc':
                    expression = []
                    for item in function:
                        if isinstance(item, list):
                            expression.append(('%s' if item[0] == 'exec' else '$(%s)') % makeexec(item[0], item[1:]))
                        else:
                            expression.append(verb(item))
                    suggestion += ' $(( %s )) ' % (' '.join(expression))
            if len(suggestion) > 0:
                suggestFunctions[name] = suggestion
        
        buf += '_opts=(\n'
        
        for group in (self.unargumented, self.argumented, self.variadic):
            for item in group:
                options = item['options']
                shortopt = []
                longopt = []
                for opt in options:
                    if len(opt) > 2:
                        if ('complete' in item) and (opt in item['complete']):
                            longopt.append(opt)
                    elif len(opt) == 2:
                        shortopt.append(opt)
                options = shortopt + longopt
                if len(longopt) == 0:
                    continue
                buf += '    \'(%s)\'{%s}' % (' '.join(options), ','.join(options))
                if 'desc' in item:
                    buf += '"["%s"]"' % verb(' '.join(item['desc']))
                if 'arg' in item:
                    buf += '":%s"' % verb(' '.join(item['arg']))
                elif options[0] in suggesters:
                    buf += '": "'
                if options[0] in suggesters:
                    suggestion = suggestFunctions[suggesters[options[0]]]
                    buf += '":( %s )"' % suggestion
                buf += '\n'
        
        buf += '    )\n\n_arguments "$_opts[@]"\n\n'
        return buf



'''
mane!

@param  shell:str   Shell to generato completion for
@param  output:str  Output file
@param  source:str  Source file
'''
def main(shell, output, source):
    with open(source, 'rb') as file:
        source = file.read().decode('utf8', 'replace')
    source = Parser.parse(source)
    Parser.simplify(source)
    
    program = source[0]
    unargumented = []
    argumented = []
    variadic = []
    suggestion = []
    default = None
    
    for item in source[1:]:
        if item[0] == 'unargumented':
            unargumented.append(item[1:]);
        elif item[0] == 'argumented':
            argumented.append(item[1:]);
        elif item[0] == 'variadic':
            variadic.append(item[1:]);
        elif item[0] == 'suggestion':
            suggestion.append(item[1:]);
        elif item[0] == 'default':
            default = item[1:];
    
    for group in (unargumented, argumented, variadic):
        for index in range(0, len(group)):
            item = group[index]
            map = {}
            for elem in item:
                map[elem[0]] = elem[1:]
            group[index] = map
    if default is not None:
        map = {}
        for elem in default:
            map[elem[0]] = elem[1:]
        default = map
    
    generator = 'Generator' + shell.upper()
    generator = globals()[generator]
    generator = generator(program, unargumented, argumented, variadic, suggestion, default)
    code = generator.get()
    
    with open(output, 'wb') as file:
        file.write(code.encode('utf-8'))



'''
mane!
'''
if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("USAGE: auto-auto-complete SHELL --output OUTPUT_FILE --source SOURCE_FILE")
        exit(1)
    
    shell = sys.argv[1]
    output = None
    source = None
    
    option = None
    aliases = {'-o' : '--output',
               '-f' : '--source', '--file' : '--source',
               '-s' : '--source'}
    
    def useopt(option, arg):
        global source
        global output
        old = None
        if   option == '--output': old = output; output = arg
        elif option == '--source': old = source; source = arg
        else:
            raise Exception('Unrecognised option: ' + option)
        if old is not None:
            raise Exception('Duplicate option: ' + option)
    
    for arg in sys.argv[2:]:
        if option is not None:
            if option in aliases:
                option = aliases[option]
            useopt(option, arg)
            option = None
        else:
            if '=' in arg:
                useopt(arg[:index('=')], arg[index('=') + 1:])
            else:
                option = arg
    
    if output is None: raise Exception('Unused option: --output')
    if source is None: raise Exception('Unused option: --source')
    
    main(shell= shell, output= output, source= source)

