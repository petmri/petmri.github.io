---
title: Quantitative and qualitative analysis
---

# Quantitative and qualitative analysis

Two distinct approaches exist for reducing DCE curves to numerical measures, and they address
different questions. The first characterizes the shape of the enhancement curve. The second
estimates the physiological parameters that produced it.

## Semi-quantitative analysis

Semi-quantitative measures are computed directly from the signal intensity curve, without
conversion to concentration and without a kinetic model.

| Measure | Definition |
| --- | --- |
| **Peak enhancement** | Maximum signal increase above baseline, conventionally expressed as a percentage |
| **Wash-in slope** | Gradient of the initial upslope |
| **Time to peak** | Interval from arrival to maximum signal intensity |
| **Washout** | Behavior after the peak, classified as declining, plateau or persistent |
| **IAUC** | Initial area under the curve over a defined interval, commonly IAUC<sub>60</sub> or IAUC<sub>90</sub> |
| **Curve type** | The type I, II and III classification of persistent, plateau and washout morphology |

**Strengths.** No arterial input function, native T1 map or kinetic model is required, which
eliminates the principal failure modes of quantitative analysis. The measures tolerate coarse
temporal sampling, are computationally inexpensive, and are reproducible within an institution.
A substantial proportion of the clinical literature, and several established reporting
conventions, rest on semi-quantitative rather than pharmacokinetic measures; the curve-type
classification used in breast MRI is one such example.

**Limitations.** The measures are expressed in arbitrary units. Percentage enhancement depends
upon scanner, pulse sequence, flip angle, dose per unit body mass, injection rate and the native
T1 of the tissue. Agreement between institutions examining the same subject is accordingly poor,
as is agreement within an institution across a hardware or software change. The measures are
moreover descriptive rather than mechanistic: an increased wash-in slope establishes that
enhancement occurred more rapidly, but does not distinguish increased perfusion from increased
permeability.

## Pharmacokinetic modeling

Quantitative analysis converts signal intensity to gadolinium concentration and fits a model of
contrast exchange to the resulting curves, with reference to the measured
[arterial input function](dce-mri.md#the-arterial-input-function).

The estimated parameters are physical quantities:

| Parameter | Definition | Units |
| --- | --- | --- |
| **K<sup>trans</sup>** | Volume transfer constant between plasma and the extravascular extracellular space | min<sup>−1</sup> |
| **v<sub>e</sub>** | Extravascular extracellular volume fraction | dimensionless, 0–1 |
| **v<sub>p</sub>** | Plasma volume fraction | dimensionless, 0–1 |
| **k<sub>ep</sub>** | Efflux rate constant, equal to K<sup>trans</sup>/v<sub>e</sub> | min<sup>−1</sup> |

Model selection depends upon the tissue under examination and upon what the acquisition can
support. [ROCKETSHIP](https://dceasy.org/ROCKETSHIP/) implements the Tofts, extended Tofts,
Patlak, two-compartment exchange, fast exchange regime and tissue uptake models. For a discussion
of model differences and appropriate model selection see 
[pharmacokinetic models.](https://dceasy.org/ROCKETSHIP/reference/models/)

**Strengths.** The estimated parameters retain meaning outside the dataset in which they were
measured. K<sup>trans</sup> is in principle comparable across scanners, institutions and time
points, which is the precondition for multi-center trials and for longitudinal assessment of
treatment response. Modeling further resolves effects that curve morphology confounds: a lesion
enhancing rapidly by virtue of perfusion and one enhancing rapidly by virtue of permeability are
similar semi-quantitatively and distinguishable after fitting.

**Limitations.** The number of failure modes is considerably greater, and most are not evident
in the output.

- **An arterial input function is required**, and error in it propagates directly into
  K<sup>trans</sup>. This is the dominant error source, and motivates both
  [AutoAIF](../tools/autoaif.md) and the independent verification afforded by
  [AIFArtist](../tools/aifartist.md)
- **A native T1 map is required.** An erroneous T1 yields an erroneous concentration and hence
  an erroneous K<sup>trans</sup>, without indication of failure
- **Temporal resolution must be adequate.** Models that resolve flow require high temporal 
  resolution to resolve the bolus peak. Models without this term are more tolerant low low
  temporal resolution.
- **Model misspecification**, if the assumptions of the model are violated (e.g. no backflux
  in the Patlak model) the results will have large errors.
- **Absolute values reported in the literature vary between institutions** more than theory
  predicts, largely in consequence of the preceding factors.

## Selection

| | Semi-quantitative | Pharmacokinetic |
| --- | --- | --- |
| Arterial input function required | No | Yes |
| Native T1 map required | No | Yes |
| Units | Arbitrary | Physical |
| Comparable between institutions | No | In principle |
| Sensitivity to temporal resolution | Low | High |
| Resolves perfusion from permeability | No | Yes |
| Failure mode | Apparent | Frequently silent |

The governing consideration is the scope of the intended comparison. Multi-center studies,
longitudinal assessment of treatment response, and any analysis in which a measurement is
compared against one acquired elsewhere require parameters expressed in physical units. Where
comparison is confined to a single examination, or between lesions in one subject on one
scanner, semi-quantitative measures are robust and their failure modes are readily apparent.

!!! note "The two approaches are not mutually exclusive"

    A quantitative pipeline yields the semi-quantitative measures without additional
    acquisition, the concentration curves being already computed and IAUC being an integral of
    them. Reporting both is advisable. Where a K<sup>trans</sup> map appears anomalous, the
    semi-quantitative maps provide the most direct means of distinguishing a genuine
    physiological finding from a fitting failure, since they do not depend upon the input
    function or the T1 map that would otherwise be implicated.

    Module E of [ROCKETSHIP](https://dceasy.org/ROCKETSHIP/) supports this comparison, and each
    fit is accompanied by a goodness-of-fit map.
