# batoolset-gui

The Qt/GUI layer of [batoolset](https://github.com/baigouy/BAtoolset): vector
shapes and images for figures (`batoolset.drawings`), figure layout
(`batoolset.figure`), LUTs with an editor and inverted LUTs (`batoolset.luts`),
painting widgets and dialogs (`batoolset.GUI`, `batoolset.dialogs`,
`batoolset.pyqts`, `batoolset.uis`) and object serialization
(`batoolset.serializations`).

It installs into the same `batoolset` package as the core library, which needs
no Qt. Since 0.2.0 these modules are no longer part of `batoolset` itself.

```bash
pip install batoolset-gui
```

This installs `batoolset` (0.2.0 or later), PyQt6 and QtPy. It is used by
[PyFigures](https://github.com/baigouy/PyFigures).

## Licence

BSD 2-Clause, see [LICENSE](LICENSE).
