//! Linker arguments for the macOS extension module.
//!
//! PyO3's `extension-module` feature deliberately does not link a Python
//! library: the interpreter that loads the extension resolves those symbols.
//! macOS refuses undefined symbols by default, so the cdylib needs
//! `-undefined dynamic_lookup`.
//!
//! Maturin passes that argument automatically, which is why the installed
//! extension builds. A manual cargo build does not, which is why
//! `cargo build`, `cargo test` and the `symbol-surface-load-v0` profile all
//! failed on macOS with undefined `_PyBaseObject_Type`, `__Py_IncRef` and
//! `__Py_NoneStruct`. PyO3's own guide prescribes this build script for manual
//! builds; on every other platform it emits nothing, and on Linux the link
//! already succeeds because undefined symbols are permitted in a shared object.
//!
//! This is why `pyo3-build-config` is a build dependency: the call is the
//! supported way to obtain the arguments, and it keeps them correct for targets
//! this repository does not currently build.

fn main() {
    pyo3_build_config::add_extension_module_link_args();
}
