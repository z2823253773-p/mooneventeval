# Sources and third-party notices

MoonEventEval's own source and documentation use the [MIT license](LICENSE).
Copyright attribution uses the repository's existing author name, Hengrui Zhang.
The three JSON examples are synthetic fixtures created for this project; they
contain no recordings, downloaded benchmark data or clinical data.

The product imports `moonbitlang/core` from the pinned local MoonBit toolchain
`0.10.14+7d59c7ec9`. Its local module manifest declares Apache-2.0. The unchanged
[core license](LICENSES/moonbit-core-LICENSE) and
[core notices](LICENSES/moonbit-core-NOTICE) are preserved, including upstream
notices for adapted algorithms. Core sources, compiler binaries and runtime
archives are not bundled in this source candidate. Native builds may link
MoonBit runtime/core components; these notices do not relicense those components
as MIT. Toolchain downloads retain their upstream terms.

The native I/O adapter is project code using platform C/POSIX interfaces. No
third-party C implementation is copied into the candidate.

Original `sed_eval` commit `0cb1b6d11ceec4fe500cc9b31079c9d8666ed6eb`
(MIT) is used only in the separate development reference environment. Its
algorithm/source and its Python dependencies are not included in this candidate
or imported by the product. See [validation scope](VALIDATION.md). No claim is
made that the product uses its raw global metric definitions unchanged.
