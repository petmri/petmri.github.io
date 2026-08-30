---
title: DCE-MRI in Brief
---

# What is DCE-MRI

Dynamic contrast-enhanced MRI comprises a single 4D acquisition in which one T1-weighted image is
repeatedly acquired before, during and after intravenous administration of a gadolinium-based
contrast agent. A typical protocol acquires 5 to 100 frames at a temporal resolution of
2 to 60 seconds, covering five to fifteen minutes in total.

Gadolinium shortens the longitudinal relaxation time and therefore increase signal intensity on
T1-weighted sequences. In DCE signal intensity therefore increases where contrast arrives and declines
as it clears. Each voxel yields a signal-versus-time curve, and it is this curve, rather than
any individual frame, that constitutes the measurement.

## Determinants of the tissue curve

Three physiological factors govern the shape of a tissue curve.

**Delivery** determines how much contrast reaches the voxel and how rapidly, and reflects
tissue perfusion. **Permeability** determines the rate at which contrast crosses the vessel
wall into the surrounding tissue. In healthy brain this is negligible, in other tissues (muscle
tumor, inflammatory lesion or infarct) contrast extravasates and the tissue curve rises higher and 
persists longer (delayed washout). **Interstitial volume** determines the extravascular extracellular 
space available to the extravasatedccontrast, and therefore how much may accumulate before 
tissue and plasma equilibrate.

A curve exhibiting rapid enhancement followed by rapid washout indicates high perfusion with
limited retention. A curve enhancing slowly but monotonically indicates accumulation exceeding
clearance. These patterns form the basis of qualitative interpretation; separating the
underlying parameters is the object of pharmacokinetic modeling.

## The arterial input function

A tissue curve cannot be interpreted in isolation, because its shape depends on the quantity of
contrast delivered as well as on the properties of the tissue. Two voxels of identical
physiology yield different curves if injection rate, cardiac output or dose per unit body mass
differ between the subjects examined.

The arterial input function, the concentration-time curve measured in a feeding artery,
quantifies this. Deconvolving the tissue response with respect to the input yields a
result attributable to the tissue rather than to the administration. Error in the input
function is the dominant source of systematic error in quantitative DCE-MRI, so extra care
for its determination is warranted.

## Conversion of signal intensity to concentration

Signal intensity is expressed in arbitrary units. It depends upon the scanner, the receive
coil, the pulse sequence and the receiver gain, and additionally upon the native T1 of the
tissue, which varies between tissues and between subjects.

Conversion to gadolinium concentration requires two further quantities:

- the **pre-contrast T1** of each voxel, typically derived from a variable flip angle series acquired before
  contrast administration. This is the output of
  [parametric_scripts](../tools/parametric_scripts.md) and of the T1 mapping stage of
  [DCEPrep](https://dceasy.org/DCEPrep/)
- the **relaxivity** of the contrast agent used

Physical interpretation of the derived parameters is valid only after this conversion. The
preceding stages of the pipeline, namely motion correction, T1 mapping and input function
determination, exist to render the conversion reliable.

## Acquisition requirements

Quantitative analysis requires three acquisitions, which are those converted by
[dce2bids](../tools/dce2bids.md):

| Acquisition | Description | Purpose |
| --- | --- | --- |
| **DCE** | The 4D dynamic series | The measurement itself |
| **VFA** | Multiple flip angles, pre-contrast | Native T1 map for conversion to concentration |
| **Structural** | Typically a T1 MPRAGE | Anatomical reference for registration and region definition |

Two acquisition parameters constrain all subsequent analysis. **Temporal resolution** determines
which models may be fitted: the vascular contribution is carried by the initial rapid upslope,
and a series sampled too coarsely to resolve it cannot support estimation of blood flow
irrespective of the fitting procedure employed. **Acquisition duration** determines how well the
slower extravasation component is constrained; a series terminated prematurely leaves the
washout phase under-sampled.

## Related

- [Quantitative and qualitative analysis](quantitative-analysis.md), on the interpretation of
  the resulting curves
- [The expected BIDS layout](bids-layout.md), on the organization of a study on disk
