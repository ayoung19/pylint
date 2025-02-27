# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/PyCQA/pylint/blob/main/CONTRIBUTORS.txt

"""Checkers for various standard library functions."""

from __future__ import annotations

import sys
from collections.abc import Iterable
from typing import TYPE_CHECKING

import astroid
from astroid import nodes

from pylint import interfaces
from pylint.checkers import BaseChecker, DeprecatedMixin, utils

if TYPE_CHECKING:
    from pylint.lint import PyLinter

OPEN_FILES_MODE = ("open", "file")
OPEN_FILES_ENCODING = ("open", "read_text", "write_text")
UNITTEST_CASE = "unittest.case"
THREADING_THREAD = "threading.Thread"
COPY_COPY = "copy.copy"
OS_ENVIRON = "os._Environ"
ENV_GETTERS = ("os.getenv",)
SUBPROCESS_POPEN = "subprocess.Popen"
SUBPROCESS_RUN = "subprocess.run"
OPEN_MODULE = {"_io", "pathlib"}
DEBUG_BREAKPOINTS = ("builtins.breakpoint", "sys.breakpointhook", "pdb.set_trace")
LRU_CACHE = {
    "functools.lru_cache",  # Inferred for @lru_cache
    "functools._lru_cache_wrapper.wrapper",  # Inferred for @lru_cache() on >= Python 3.8
    "functools.lru_cache.decorating_function",  # Inferred for @lru_cache() on <= Python 3.7
}
NON_INSTANCE_METHODS = {"builtins.staticmethod", "builtins.classmethod"}


# For modules, see ImportsChecker

DEPRECATED_ARGUMENTS = {
    (0, 0, 0): {
        "int": ((None, "x"),),
        "bool": ((None, "x"),),
        "float": ((None, "x"),),
    },
    (3, 8, 0): {
        "asyncio.tasks.sleep": ((None, "loop"),),
        "asyncio.tasks.gather": ((None, "loop"),),
        "asyncio.tasks.shield": ((None, "loop"),),
        "asyncio.tasks.wait_for": ((None, "loop"),),
        "asyncio.tasks.wait": ((None, "loop"),),
        "asyncio.tasks.as_completed": ((None, "loop"),),
        "asyncio.subprocess.create_subprocess_exec": ((None, "loop"),),
        "asyncio.subprocess.create_subprocess_shell": ((4, "loop"),),
        "gettext.translation": ((5, "codeset"),),
        "gettext.install": ((2, "codeset"),),
        "functools.partialmethod": ((None, "func"),),
        "weakref.finalize": ((None, "func"), (None, "obj")),
        "profile.Profile.runcall": ((None, "func"),),
        "cProfile.Profile.runcall": ((None, "func"),),
        "bdb.Bdb.runcall": ((None, "func"),),
        "trace.Trace.runfunc": ((None, "func"),),
        "curses.wrapper": ((None, "func"),),
        "unittest.case.TestCase.addCleanup": ((None, "function"),),
        "concurrent.futures.thread.ThreadPoolExecutor.submit": ((None, "fn"),),
        "concurrent.futures.process.ProcessPoolExecutor.submit": ((None, "fn"),),
        "contextlib._BaseExitStack.callback": ((None, "callback"),),
        "contextlib.AsyncExitStack.push_async_callback": ((None, "callback"),),
        "multiprocessing.managers.Server.create": ((None, "c"), (None, "typeid")),
        "multiprocessing.managers.SharedMemoryServer.create": (
            (None, "c"),
            (None, "typeid"),
        ),
    },
    (3, 9, 0): {"random.Random.shuffle": ((1, "random"),)},
}

DEPRECATED_DECORATORS = {
    (3, 8, 0): {"asyncio.coroutine"},
    (3, 3, 0): {
        "abc.abstractclassmethod",
        "abc.abstractstaticmethod",
        "abc.abstractproperty",
    },
    (3, 4, 0): {"importlib.util.module_for_loader"},
}


DEPRECATED_METHODS: dict = {
    0: {
        "cgi.parse_qs",
        "cgi.parse_qsl",
        "ctypes.c_buffer",
        "distutils.command.register.register.check_metadata",
        "distutils.command.sdist.sdist.check_metadata",
        "tkinter.Misc.tk_menuBar",
        "tkinter.Menu.tk_bindForTraversal",
    },
    2: {
        (2, 6, 0): {
            "commands.getstatus",
            "os.popen2",
            "os.popen3",
            "os.popen4",
            "macostools.touched",
        },
        (2, 7, 0): {
            "unittest.case.TestCase.assertEquals",
            "unittest.case.TestCase.assertNotEquals",
            "unittest.case.TestCase.assertAlmostEquals",
            "unittest.case.TestCase.assertNotAlmostEquals",
            "unittest.case.TestCase.assert_",
            "xml.etree.ElementTree.Element.getchildren",
            "xml.etree.ElementTree.Element.getiterator",
            "xml.etree.ElementTree.XMLParser.getiterator",
            "xml.etree.ElementTree.XMLParser.doctype",
        },
    },
    3: {
        (3, 0, 0): {
            "inspect.getargspec",
            "failUnlessEqual",
            "assertEquals",
            "failIfEqual",
            "assertNotEquals",
            "failUnlessAlmostEqual",
            "assertAlmostEquals",
            "failIfAlmostEqual",
            "assertNotAlmostEquals",
            "failUnless",
            "assert_",
            "failUnlessRaises",
            "failIf",
            "assertRaisesRegexp",
            "assertRegexpMatches",
            "assertNotRegexpMatches",
        },
        (3, 1, 0): {
            "base64.encodestring",
            "base64.decodestring",
            "ntpath.splitunc",
            "os.path.splitunc",
            "os.stat_float_times",
            "turtle.RawTurtle.settiltangle",
        },
        (3, 2, 0): {
            "cgi.escape",
            "configparser.RawConfigParser.readfp",
            "xml.etree.ElementTree.Element.getchildren",
            "xml.etree.ElementTree.Element.getiterator",
            "xml.etree.ElementTree.XMLParser.getiterator",
            "xml.etree.ElementTree.XMLParser.doctype",
        },
        (3, 3, 0): {
            "inspect.getmoduleinfo",
            "logging.warn",
            "logging.Logger.warn",
            "logging.LoggerAdapter.warn",
            "nntplib._NNTPBase.xpath",
            "platform.popen",
            "sqlite3.OptimizedUnicode",
            "time.clock",
        },
        (3, 4, 0): {
            "importlib.find_loader",
            "importlib.abc.Loader.load_module",
            "importlib.abc.Loader.module_repr",
            "importlib.abc.PathEntryFinder.find_loader",
            "importlib.abc.PathEntryFinder.find_module",
            "plistlib.readPlist",
            "plistlib.writePlist",
            "plistlib.readPlistFromBytes",
            "plistlib.writePlistToBytes",
        },
        (3, 4, 4): {"asyncio.tasks.async"},
        (3, 5, 0): {
            "fractions.gcd",
            "inspect.formatargspec",
            "inspect.getcallargs",
            "platform.linux_distribution",
            "platform.dist",
        },
        (3, 6, 0): {
            "importlib._bootstrap_external.FileLoader.load_module",
            "_ssl.RAND_pseudo_bytes",
        },
        (3, 7, 0): {
            "sys.set_coroutine_wrapper",
            "sys.get_coroutine_wrapper",
            "aifc.openfp",
            "threading.Thread.isAlive",
            "asyncio.Task.current_task",
            "asyncio.Task.all_task",
            "locale.format",
            "ssl.wrap_socket",
            "ssl.match_hostname",
            "sunau.openfp",
            "wave.openfp",
        },
        (3, 8, 0): {
            "gettext.lgettext",
            "gettext.ldgettext",
            "gettext.lngettext",
            "gettext.ldngettext",
            "gettext.bind_textdomain_codeset",
            "gettext.NullTranslations.output_charset",
            "gettext.NullTranslations.set_output_charset",
            "threading.Thread.isAlive",
        },
        (3, 9, 0): {
            "binascii.b2a_hqx",
            "binascii.a2b_hqx",
            "binascii.rlecode_hqx",
            "binascii.rledecode_hqx",
        },
        (3, 10, 0): {
            "_sqlite3.enable_shared_cache",
            "importlib.abc.Finder.find_module",
            "pathlib.Path.link_to",
            "zipimport.zipimporter.load_module",
            "zipimport.zipimporter.find_module",
            "zipimport.zipimporter.find_loader",
            "threading.currentThread",
            "threading.activeCount",
            "threading.Condition.notifyAll",
            "threading.Event.isSet",
            "threading.Thread.setName",
            "threading.Thread.getName",
            "threading.Thread.isDaemon",
            "threading.Thread.setDaemon",
            "cgi.log",
        },
        (3, 11, 0): {
            "locale.getdefaultlocale",
            "unittest.TestLoader.findTestCases",
            "unittest.TestLoader.loadTestsFromTestCase",
            "unittest.TestLoader.getTestCaseNames",
        },
    },
}


DEPRECATED_CLASSES = {
    (3, 2, 0): {
        "configparser": {
            "LegacyInterpolation",
            "SafeConfigParser",
        },
    },
    (3, 3, 0): {
        "importlib.abc": {
            "Finder",
        },
        "pkgutil": {
            "ImpImporter",
            "ImpLoader",
        },
        "collections": {
            "Awaitable",
            "Coroutine",
            "AsyncIterable",
            "AsyncIterator",
            "AsyncGenerator",
            "Hashable",
            "Iterable",
            "Iterator",
            "Generator",
            "Reversible",
            "Sized",
            "Container",
            "Callable",
            "Collection",
            "Set",
            "MutableSet",
            "Mapping",
            "MutableMapping",
            "MappingView",
            "KeysView",
            "ItemsView",
            "ValuesView",
            "Sequence",
            "MutableSequence",
            "ByteString",
        },
    },
    (3, 9, 0): {
        "smtpd": {
            "MailmanProxy",
        }
    },
    (3, 11, 0): {
        "webbrowser": {
            "MacOSX",
        },
    },
}


def _check_mode_str(mode):
    # check type
    if not isinstance(mode, str):
        return False
    # check syntax
    modes = set(mode)
    _mode = "rwatb+Ux"
    creating = "x" in modes
    if modes - set(_mode) or len(mode) > len(modes):
        return False
    # check logic
    reading = "r" in modes
    writing = "w" in modes
    appending = "a" in modes
    text = "t" in modes
    binary = "b" in modes
    if "U" in modes:
        if writing or appending or creating:
            return False
        reading = True
    if text and binary:
        return False
    total = reading + writing + appending + creating
    if total > 1:
        return False
    if not (reading or writing or appending or creating):
        return False
    return True


class StdlibChecker(DeprecatedMixin, BaseChecker):
    name = "stdlib"

    msgs = {
        "W1501": (
            '"%s" is not a valid mode for open.',
            "bad-open-mode",
            "Python supports: r, w, a[, x] modes with b, +, "
            "and U (only with r) options. "
            "See https://docs.python.org/3/library/functions.html#open",
        ),
        "W1502": (
            "Using datetime.time in a boolean context.",
            "boolean-datetime",
            "Using datetime.time in a boolean context can hide "
            "subtle bugs when the time they represent matches "
            "midnight UTC. This behaviour was fixed in Python 3.5. "
            "See https://bugs.python.org/issue13936 for reference.",
            {"maxversion": (3, 5)},
        ),
        "W1503": (
            "Redundant use of %s with constant value %r",
            "redundant-unittest-assert",
            "The first argument of assertTrue and assertFalse is "
            "a condition. If a constant is passed as parameter, that "
            "condition will be always true. In this case a warning "
            "should be emitted.",
        ),
        "W1505": (
            "Using deprecated method %s()",
            "deprecated-method",
            "The method is marked as deprecated and will be removed in "
            "a future version of Python. Consider looking for an "
            "alternative in the documentation.",
        ),
        "W1506": (
            "threading.Thread needs the target function",
            "bad-thread-instantiation",
            "The warning is emitted when a threading.Thread class "
            "is instantiated without the target function being passed. "
            "By default, the first parameter is the group param, not the target param.",
        ),
        "W1507": (
            "Using copy.copy(os.environ). Use os.environ.copy() instead. ",
            "shallow-copy-environ",
            "os.environ is not a dict object but proxy object, so "
            "shallow copy has still effects on original object. "
            "See https://bugs.python.org/issue15373 for reference.",
        ),
        "E1507": (
            "%s does not support %s type argument",
            "invalid-envvar-value",
            "Env manipulation functions support only string type arguments. "
            "See https://docs.python.org/3/library/os.html#os.getenv.",
        ),
        "W1508": (
            "%s default type is %s. Expected str or None.",
            "invalid-envvar-default",
            "Env manipulation functions return None or str values. "
            "Supplying anything different as a default may cause bugs. "
            "See https://docs.python.org/3/library/os.html#os.getenv.",
        ),
        "W1509": (
            "Using preexec_fn keyword which may be unsafe in the presence "
            "of threads",
            "subprocess-popen-preexec-fn",
            "The preexec_fn parameter is not safe to use in the presence "
            "of threads in your application. The child process could "
            "deadlock before exec is called. If you must use it, keep it "
            "trivial! Minimize the number of libraries you call into."
            "https://docs.python.org/3/library/subprocess.html#popen-constructor",
        ),
        "W1510": (
            "Using subprocess.run without explicitly set `check` is not recommended.",
            "subprocess-run-check",
            "The check parameter should always be used with explicitly set "
            "`check` keyword to make clear what the error-handling behavior is."
            "https://docs.python.org/3/library/subprocess.html#subprocess.run",
        ),
        "W1511": (
            "Using deprecated argument %s of method %s()",
            "deprecated-argument",
            "The argument is marked as deprecated and will be removed in the future.",
        ),
        "W1512": (
            "Using deprecated class %s of module %s",
            "deprecated-class",
            "The class is marked as deprecated and will be removed in the future.",
        ),
        "W1513": (
            "Using deprecated decorator %s()",
            "deprecated-decorator",
            "The decorator is marked as deprecated and will be removed in the future.",
        ),
        "W1514": (
            "Using open without explicitly specifying an encoding",
            "unspecified-encoding",
            "It is better to specify an encoding when opening documents. "
            "Using the system default implicitly can create problems on other operating systems. "
            "See https://peps.python.org/pep-0597/",
        ),
        "W1515": (
            "Leaving functions creating breakpoints in production code is not recommended",
            "forgotten-debug-statement",
            "Calls to breakpoint(), sys.breakpointhook() and pdb.set_trace() should be removed "
            "from code that is not actively being debugged.",
        ),
        "W1518": (
            "'lru_cache(maxsize=None)' or 'cache' will keep all method args alive indefinitely, including 'self'",
            "method-cache-max-size-none",
            "By decorating a method with lru_cache or cache the 'self' argument will be linked to "
            "the function and therefore never garbage collected. Unless your instance "
            "will never need to be garbage collected (singleton) it is recommended to refactor "
            "code to avoid this pattern or add a maxsize to the cache."
            "The default value for maxsize is 128.",
            {
                "old_names": [
                    ("W1516", "lru-cache-decorating-method"),
                    ("W1517", "cache-max-size-none"),
                ]
            },
        ),
    }

    def __init__(self, linter: PyLinter) -> None:
        BaseChecker.__init__(self, linter)
        self._deprecated_methods: set[str] = set()
        self._deprecated_arguments: dict[str, tuple[tuple[int | None, str], ...]] = {}
        self._deprecated_classes: dict[str, set[str]] = {}
        self._deprecated_decorators: set[str] = set()

        for since_vers, func_list in DEPRECATED_METHODS[sys.version_info[0]].items():
            if since_vers <= sys.version_info:
                self._deprecated_methods.update(func_list)
        for since_vers, func_list in DEPRECATED_ARGUMENTS.items():
            if since_vers <= sys.version_info:
                self._deprecated_arguments.update(func_list)
        for since_vers, class_list in DEPRECATED_CLASSES.items():
            if since_vers <= sys.version_info:
                self._deprecated_classes.update(class_list)
        for since_vers, decorator_list in DEPRECATED_DECORATORS.items():
            if since_vers <= sys.version_info:
                self._deprecated_decorators.update(decorator_list)
        # Modules are checked by the ImportsChecker, because the list is
        # synced with the config argument deprecated-modules

    def _check_bad_thread_instantiation(self, node):
        if not node.kwargs and not node.keywords and len(node.args) <= 1:
            self.add_message("bad-thread-instantiation", node=node)

    def _check_for_preexec_fn_in_popen(self, node):
        if node.keywords:
            for keyword in node.keywords:
                if keyword.arg == "preexec_fn":
                    self.add_message("subprocess-popen-preexec-fn", node=node)

    def _check_for_check_kw_in_run(self, node):
        kwargs = {keyword.arg for keyword in (node.keywords or ())}
        if "check" not in kwargs:
            self.add_message("subprocess-run-check", node=node)

    def _check_shallow_copy_environ(self, node: nodes.Call) -> None:
        arg = utils.get_argument_from_call(node, position=0)
        try:
            inferred_args = arg.inferred()
        except astroid.InferenceError:
            return
        for inferred in inferred_args:
            if inferred.qname() == OS_ENVIRON:
                self.add_message("shallow-copy-environ", node=node)
                break

    @utils.only_required_for_messages(
        "bad-open-mode",
        "redundant-unittest-assert",
        "deprecated-method",
        "deprecated-argument",
        "bad-thread-instantiation",
        "shallow-copy-environ",
        "invalid-envvar-value",
        "invalid-envvar-default",
        "subprocess-popen-preexec-fn",
        "subprocess-run-check",
        "deprecated-class",
        "unspecified-encoding",
        "forgotten-debug-statement",
    )
    def visit_call(self, node: nodes.Call) -> None:
        """Visit a Call node."""
        self.check_deprecated_class_in_call(node)
        for inferred in utils.infer_all(node.func):
            if inferred is astroid.Uninferable:
                continue
            if inferred.root().name in OPEN_MODULE:
                if (
                    isinstance(node.func, nodes.Name)
                    and node.func.name in OPEN_FILES_MODE
                ):
                    self._check_open_mode(node)
                if (
                    isinstance(node.func, nodes.Name)
                    and node.func.name in OPEN_FILES_ENCODING
                    or isinstance(node.func, nodes.Attribute)
                    and node.func.attrname in OPEN_FILES_ENCODING
                ):
                    self._check_open_encoded(node, inferred.root().name)
            elif inferred.root().name == UNITTEST_CASE:
                self._check_redundant_assert(node, inferred)
            elif isinstance(inferred, nodes.ClassDef):
                if inferred.qname() == THREADING_THREAD:
                    self._check_bad_thread_instantiation(node)
                elif inferred.qname() == SUBPROCESS_POPEN:
                    self._check_for_preexec_fn_in_popen(node)
            elif isinstance(inferred, nodes.FunctionDef):
                name = inferred.qname()
                if name == COPY_COPY:
                    self._check_shallow_copy_environ(node)
                elif name in ENV_GETTERS:
                    self._check_env_function(node, inferred)
                elif name == SUBPROCESS_RUN:
                    self._check_for_check_kw_in_run(node)
                elif name in DEBUG_BREAKPOINTS:
                    self.add_message("forgotten-debug-statement", node=node)
            self.check_deprecated_method(node, inferred)

    @utils.only_required_for_messages("boolean-datetime")
    def visit_unaryop(self, node: nodes.UnaryOp) -> None:
        if node.op == "not":
            self._check_datetime(node.operand)

    @utils.only_required_for_messages("boolean-datetime")
    def visit_if(self, node: nodes.If) -> None:
        self._check_datetime(node.test)

    @utils.only_required_for_messages("boolean-datetime")
    def visit_ifexp(self, node: nodes.IfExp) -> None:
        self._check_datetime(node.test)

    @utils.only_required_for_messages("boolean-datetime")
    def visit_boolop(self, node: nodes.BoolOp) -> None:
        for value in node.values:
            self._check_datetime(value)

    @utils.only_required_for_messages("method-cache-max-size-none")
    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        if node.decorators and isinstance(node.parent, nodes.ClassDef):
            self._check_lru_cache_decorators(node.decorators)

    def _check_lru_cache_decorators(self, decorators: nodes.Decorators) -> None:
        """Check if instance methods are decorated with functools.lru_cache."""
        lru_cache_nodes: list[nodes.NodeNG] = []
        for d_node in decorators.nodes:
            try:
                for infered_node in d_node.infer():
                    q_name = infered_node.qname()
                    if q_name in NON_INSTANCE_METHODS:
                        return

                    # Check if there is a maxsize argument set to None in the call
                    if q_name in LRU_CACHE and isinstance(d_node, nodes.Call):
                        try:
                            arg = utils.get_argument_from_call(
                                d_node, position=0, keyword="maxsize"
                            )
                        except utils.NoSuchArgumentError:
                            break

                        if not isinstance(arg, nodes.Const) or arg.value is not None:
                            break

                        lru_cache_nodes.append(d_node)
                        break

                    if q_name == "functools.cache":
                        lru_cache_nodes.append(d_node)
                        break
            except astroid.InferenceError:
                pass
        for lru_cache_node in lru_cache_nodes:
            self.add_message(
                "method-cache-max-size-none",
                node=lru_cache_node,
                confidence=interfaces.INFERENCE,
            )

    def _check_redundant_assert(self, node, infer):
        if (
            isinstance(infer, astroid.BoundMethod)
            and node.args
            and isinstance(node.args[0], nodes.Const)
            and infer.name in {"assertTrue", "assertFalse"}
        ):
            self.add_message(
                "redundant-unittest-assert",
                args=(infer.name, node.args[0].value),
                node=node,
            )

    def _check_datetime(self, node):
        """Check that a datetime was inferred, if so, emit boolean-datetime warning."""
        try:
            inferred = next(node.infer())
        except astroid.InferenceError:
            return
        if (
            isinstance(inferred, astroid.Instance)
            and inferred.qname() == "datetime.time"
        ):
            self.add_message("boolean-datetime", node=node)

    def _check_open_mode(self, node: nodes.Call):
        """Check that the mode argument of an open or file call is valid."""
        try:
            mode_arg = utils.get_argument_from_call(node, position=1, keyword="mode")
        except utils.NoSuchArgumentError:
            return
        if mode_arg:
            mode_arg = utils.safe_infer(mode_arg)
            if isinstance(mode_arg, nodes.Const) and not _check_mode_str(
                mode_arg.value
            ):
                self.add_message(
                    "bad-open-mode",
                    node=node,
                    args=mode_arg.value or str(mode_arg.value),
                )

    def _check_open_encoded(self, node: nodes.Call, open_module: str) -> None:
        """Check that the encoded argument of an open call is valid."""
        mode_arg = None
        try:
            if open_module == "_io":
                mode_arg = utils.get_argument_from_call(
                    node, position=1, keyword="mode"
                )
            elif open_module == "pathlib":
                mode_arg = utils.get_argument_from_call(
                    node, position=0, keyword="mode"
                )
        except utils.NoSuchArgumentError:
            pass

        if mode_arg:
            mode_arg = utils.safe_infer(mode_arg)

        if (
            not mode_arg
            or isinstance(mode_arg, nodes.Const)
            and (not mode_arg.value or "b" not in str(mode_arg.value))
        ):
            encoding_arg = None
            try:
                if open_module == "pathlib":
                    if node.func.attrname == "read_text":
                        encoding_arg = utils.get_argument_from_call(
                            node, position=0, keyword="encoding"
                        )
                    elif node.func.attrname == "write_text":
                        encoding_arg = utils.get_argument_from_call(
                            node, position=1, keyword="encoding"
                        )
                    else:
                        encoding_arg = utils.get_argument_from_call(
                            node, position=2, keyword="encoding"
                        )
                else:
                    encoding_arg = utils.get_argument_from_call(
                        node, position=3, keyword="encoding"
                    )
            except utils.NoSuchArgumentError:
                self.add_message("unspecified-encoding", node=node)

            if encoding_arg:
                encoding_arg = utils.safe_infer(encoding_arg)

                if isinstance(encoding_arg, nodes.Const) and encoding_arg.value is None:
                    self.add_message("unspecified-encoding", node=node)

    def _check_env_function(self, node, infer):
        env_name_kwarg = "key"
        env_value_kwarg = "default"
        if node.keywords:
            kwargs = {keyword.arg: keyword.value for keyword in node.keywords}
        else:
            kwargs = None
        if node.args:
            env_name_arg = node.args[0]
        elif kwargs and env_name_kwarg in kwargs:
            env_name_arg = kwargs[env_name_kwarg]
        else:
            env_name_arg = None

        if env_name_arg:
            self._check_invalid_envvar_value(
                node=node,
                message="invalid-envvar-value",
                call_arg=utils.safe_infer(env_name_arg),
                infer=infer,
                allow_none=False,
            )

        if len(node.args) == 2:
            env_value_arg = node.args[1]
        elif kwargs and env_value_kwarg in kwargs:
            env_value_arg = kwargs[env_value_kwarg]
        else:
            env_value_arg = None

        if env_value_arg:
            self._check_invalid_envvar_value(
                node=node,
                infer=infer,
                message="invalid-envvar-default",
                call_arg=utils.safe_infer(env_value_arg),
                allow_none=True,
            )

    def _check_invalid_envvar_value(self, node, infer, message, call_arg, allow_none):
        if call_arg in (astroid.Uninferable, None):
            return

        name = infer.qname()
        if isinstance(call_arg, nodes.Const):
            emit = False
            if call_arg.value is None:
                emit = not allow_none
            elif not isinstance(call_arg.value, str):
                emit = True
            if emit:
                self.add_message(message, node=node, args=(name, call_arg.pytype()))
        else:
            self.add_message(message, node=node, args=(name, call_arg.pytype()))

    def deprecated_methods(self):
        return self._deprecated_methods

    def deprecated_arguments(self, method: str):
        return self._deprecated_arguments.get(method, ())

    def deprecated_classes(self, module: str):
        return self._deprecated_classes.get(module, ())

    def deprecated_decorators(self) -> Iterable:
        return self._deprecated_decorators


def register(linter: PyLinter) -> None:
    linter.register_checker(StdlibChecker(linter))
