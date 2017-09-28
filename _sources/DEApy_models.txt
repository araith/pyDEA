.. role:: raw-latex(raw)
   :format: latex
..

Models Used
===========

These are a selection of the various models that DEApy can run. First, we define some notation.
 We assume there are :math:`m` inputs, :math:`n` outputs and :math:`s` DMUs. 
The set of inputs is :math:`I = \left \{ 1,\ldots,m \right \}`, 
the set of outputs is :math:`O = \left \{ 1,\ldots,n \right \}` and the set of DMUs is :math:`S= \left \{1,...,s \right \}`. 
The inputs are represented by a :math:`s \times m` matrix :math:`X`, where :math:`x_i` is a column vector of inputs associated with DMU :math:`i`, and :math:`x_{ij}` represents the amount the :math:`i` th  DMU uses of input :math:`j`. The outputs are represented by a :math:`s \times n` matrix :math:`Y`, where :math:`y_i` is a column  vector of outputs associated with DMU :math:`i` and :math:`y_{ij}` represents the amount the :math:`i` th DMU produces of output :math:`j`. Vector :math:`\nu` represents a row vector of input weights, and :math:`\mu` is a row vector of output weights associated  with the multiplier form of DEA. Vector :math:`\lambda` is a column vector of composite weights, associated with the envelopment form of DEA.
Let :math:`\epsilon` be a non-Archimedean element, i.e., a number smaller than any positive real number.
Let :math:`s^+_i` and :math:`s^-` be a vector of slack variables for the outputs and inputs, respectively.
Standard Models
---------------

Here are the standard, regular DEA models that can be found in any standard DEA textbook. We used [CSZ04]_ and [CCLS94]_.

Multiplier - Input Orientation

.. math::

   \begin{array}{rl}
   \label{equ:mult_in}
   max & \sum\limits_{j \in O} \mu_j y_{oj} \\ 
   st: & \sum\limits_{i \in I} \nu_i x_{oi}=1\\
   &-\sum\limits_{i \in I} \nu_i x_{ri} + \sum\limits_{j \in O} \mu_j y_{rj}\leq 0, \quad r=1,2,...,s\\
   &\mu_j,\nu_i\geq \epsilon, j \in O, i \in I. 
   \end{array}

Envelopment - Input Orientation

.. math::

   \begin{array}{rl}
   \label{eq:env_in}
   min & \theta-\epsilon(\sum\limits_{i \in I}s^- + \sum\limits_{j \in O}s^+) \\
   st: &\theta x_{oi} -\sum\limits_{r \in S} x_{ri} \lambda_r - s^-_i = 0,\text{ for } i \in I\\
    & \sum\limits_{r \in S} y_{rj}\lambda_r - s^+_j =  y_{oj},\text{ for } j \in O\\
   &\lambda_r,s^+_j,s^-_i\geq 0, r \in S, i \in I, j \in O.
   \end{array}

Here, we swap to output orientation - that is, we keep inputs constant, and determine what augmentation in outputs is required for a DMU is become efficient.

Multiplier - Output Orientation

.. math::

   \begin{array}{rl}
   min~~~ & \sum\limits_{i \in I} \nu_i x_{oi}\\ 
   st: ~~~& \sum\limits_{j \in O} \mu_j y_{oj}=1\\
   &\sum\limits_{i \in I} \nu_i x_{ri}-\sum\limits_{j \in O} \mu_j y_{rj}\geq 0, r\in S\\
   &\mu_j,\nu_i\geq \epsilon, j \in O, i \in I. 
   \end{array}

Envelopment - Output Orientation

.. math::

   \begin{array}{rl}
   max~~ & \phi+\epsilon(\sum\limits_{i \in I}s_i^- + \sum\limits_{j \in O}s_j^+) \\
   st: ~~&\sum\limits_{r \in S}x_{ri}\lambda_r + s_i^- = x_{oi},\text{ for } i \in I\\
   & \phi y_{oj}-\sum\limits_{r\in S} y_{rj}\lambda_r + s^+_j = 0,\text{ for } j \in O\\
   &\lambda_r,s^+_j,s^-_i\geq 0, r \in S, i \in I, j \in O.
   \end{array}

Variable Returns to Scale
-------------------------

Previous models assumed that all firms were operating at an optimal
scale (the *Constant Returns to Scale* assumption). Use of this
assumption in situations where it is not warranted leads to efficiency
scores that includes the effect of scale efficiencies. Hence, the
following changes are proposed to create the VRS model:

-  The addition of an extra variable to the multiplier model - the sign
   of this term can provide extra information about the returns to scale
   on the firms part of the frontier.

-  The addition of an extra constraint to the envelopment model - to
   ensure the sum of the :math:`\lambda` weights equal one.

Multiplier - Input Orientation, VRS

.. math::

   \begin{array}{rl}
   max~~~ & \sum\limits_{j \in O} \mu_j y_{oj}+\omega_o \\ 
   st: ~~~& \sum\limits_{i \in I} \nu_i x_{oi}=1\\
   &-\sum\limits_{i \in I} \nu_i x_{ri}+\sum\limits_{j \in O} \mu_j y_{rj}+\omega_o\leq 0, r \in S\\
   &\mu_j,\nu_i\geq \epsilon, j \in O, i \in I.
   \end{array}

Envelopment - Input Orientation, VRS

.. math::

   \begin{array}{rl}
   \label{eq:env_in}
   min & \theta-\epsilon(\sum\limits_{i \in I}s^- + \sum\limits_{j \in O}s^+), \\
   st: ~~&\theta x_{oi} -\sum\limits_{r \in S} x_{ri} \lambda_r - s^-_i = 0,\text{ for } i \in I\\
    & \sum\limits_{r \in S} y_{rj}\lambda_r - s^+_j = y_{oj},\text{ for } j \in O\\
    &\sum\limits_{r\in S}\lambda_r=1\\
   &\lambda_r,s^+_j,s^-_i\geq 0, r \in S, i \in I, j \in O.
   \end{array}

Multiplier - Output Orientation, VRS

.. math::

   \begin{array}{rl}
   min_{\mu, \nu}~~~ & \sum\limits_{i \in I} \nu_i x_{oi}+\omega_o, \\ 
   st: ~~~& \sum\limits_{j \in O} \mu_j y_{oj}=1,\\
   &\sum\limits_{i \in I} \nu_i x_{ri}-\sum\limits_{j \in O} \mu_j y_{rj} + \omega_o\geq 0, r\in S\\
   &\mu_j,\nu_i\geq \epsilon, j \in O, i \in I 
   \end{array}

Envelopment - Output Orientation, VRS

.. math::

   \begin{array}{rl}
   max~~ & \phi+\epsilon(\sum\limits_{i \in I}s_i^- + \sum\limits_{j \in O}s_j^+) \\
   st: ~~&\sum\limits_{r \in S}x_{ri}\lambda_r + s_i^- = x_{oi},\text{ for } i \in I\\
   & \phi y_{oj}-\sum\limits_{r\in S} y_{rj}\lambda_r + s^+_j = 0,\text{ for } j \in O\\
   &\sum\limits_{r\in S}\lambda_r=1\\
   &\lambda_r,s^+_j,s^-_i\geq 0, r \in S, i \in I, j \in O.
   \end{array}

Non-Discretionary Variables
---------------------------

Often, the manager of a DMU will only be able to reduce consumption of some of the inputs. For example, consider the case of an electronics factory in China. It is reasonable to assume they can control the usage of variable inputs such as labour and materials, but can't easy control fixed inputs, such as their land and building size (in the short term). Hence, the question becomes - what reduction in variable input usage can be achieved, given a constant level of outputs and fixed inputs. For notation purposes, if input :math:`i` is discretionary, then :math:`i \in I_D`, else :math:`i \in I_{ND}`. If output :math:`j` is discretionary, then :math:`j \in O_D`, otherwise :math:`j \in O_{ND}`.

Multiplier - Input Orientation, non-discretionary Inputs

.. math::

   \begin{array}{rl}
   max~~~ & - \sum\limits_{i \in I_{ND}} \nu_i x_{oi} + \sum\limits_{j \in O} \mu_j y_{oj} \\ 
   st: ~~~& \sum\limits_{i \in D} \nu_i x_{oi}=1,\\
   &-\sum\limits_{i \in I_D} \nu_i x_{ri}-\sum\limits_{i \in I_{ND}} \nu_i x_{ri} + \sum\limits_{j \in O} \mu_j y_{rj}\leq 0, r \in S\\
   &\mu_j,\nu_i\geq \epsilon, j \in O, i \in \{I_D,I_{ND} \}.
   \end{array}

Envelopment - Input Orientation, non-discretionary Inputs

.. math::

   \begin{array}{rl}
   min~~ & \theta-\epsilon(\sum\limits_{i \in I_D}s^-_i + \sum\limits_{i \in I_{ND}}s^-_i + \sum\limits_{j \in O}s^+_j) \\
   st: ~~&\theta x_{oi} -\sum\limits_{r\in S} x_{ri} \lambda_r - s_i^- = 0, i \in I_{D}\\
   & -\sum\limits_{r\in S} x_{ri} \lambda_r - s_i^- = -x_{oi}, i \in I_{ND}\\
    & \sum\limits_{r\in S}y_{rj}\lambda_r - s_j^+ = y_{oj},j \in O\\
   &\lambda_r,s^+_j,s^-_i\geq 0, r \in S, i \in \{I_D,I_{ND} \}, j \in O.
   \end{array}

Multiplier - Output Orientation, non-discretionary Outputs

.. math::

   \begin{array}{rl}
   min~~~ & \sum\limits_{i \in I} \nu_i x_{oi} - \sum\limits_{j \in O_{ND}} \mu_j y_{oj} \\ 
    st: ~~~& \sum\limits_{j \in O} \mu_j y_{oj}=1 \\
     &\sum\limits_{i \in I} \nu_i x_{ri} - \sum\limits_{j \in \{ O_D,O_{ND} \}} \mu_j y_{rj}\geq 0, r\in S\\
    &\mu_j,\nu_i\geq \epsilon, j \in \{ O_D,O_{ND} \}, i \in I. 
   \end{array}

Envelopment - Output Orientation, non-discretionary Outputs

.. math::

   \begin{array}{rl}
   max~~ & \phi+\epsilon(\sum\limits_{i \in I}s_i^+ + \sum\limits_{j \in \{ O_D,O_{ND} \}s_j^-} \\
   st: ~~&\sum\limits_{r \in S}x_{ri}\lambda_r + s_i^- = x_{oi},\text{ for } i \in I\\
   & \phi y_{oj}-\sum\limits_{r\in S} y_{rj}\lambda_r + s^+_j = 0,\text{ for } j \in O_D\\
    &-\sum\limits_{r\in S} y_{rj}\lambda_r + s^+_j = y_{oj},\text{ for } j \in O_{ND}\\
   &\lambda_r,s^+_j,s^-_i\geq 0, r \in S, i \in I, j \in \{ O_D,O_{ND} \}.
   \end{array}

Disposable Variables
--------------------

Previous models have assumed that DMU’s can always discard excess inputs
or outputs without cost (known as the assumption of *Strong
Disposability*). This is often advantageous to a firm, as after a
certain level each additional unit of input produces a decreasing level
of output (law of diminishing returns). Indeed, after some higher level
of inputs, additional units of inputs results in a *fall* in outputs.
This is known as input/output congestion. But sometimes external
circumstances prevent firms discarding unneeded inputs, such as union
agreements preventing a reduction in labour hours. In this case, labour
hours would be known as a *weakly disposable* category, associated with
the assumption of *Weak Disposability*. To incorporate this into DEA
models, the following changes have been proposed:

-  In the multiplier model, let the weights of the weakly disposable
   categories be unrestricted in sign.

-  In the envelopment model, remove the slack variable corresponding to the weak disposable input/output. 

For notation purposes, if input :math:`i` is strongly disposable, then :math:`i \in I_{SD}`, otherwise :math:`i \in I_{WD}`. If output :math:`j` is strongly disposable, then :math:`j \in O_{SD}`, else :math:`j \in O_{WD}`.

Multiplier - Input Orientation, Disposable Inputs/Outputs

.. math::

   \begin{array}{rl}
   max~~~ & \sum\limits_{j \in O_{SD}} \mu_j y_{oj}+\sum\limits_{j \in O_{WD}} \mu_j y_{oj}, \\ 
   st: ~~~& \sum\limits_{i \in \{ I_SD,I_WD\}} \nu_i x_{oi}=1,\\
   &-\sum\limits_{i \in \{ I_{SD},I_{WD}\}} \nu_i x_{ri}+\sum\limits_{j \in \{ O_{SD},O_{WD}\}} \mu_j y_{rj}\leq 0, r\in S\\
   &\nu_i,\mu_j\geq \epsilon ,~ i \in I_{SD},~ j \in O_{SD}\\
   & \nu_i, \mu_j \text{ unrestricted}, ~i \in I_{WD}, ~j \in O_{WD}
   \end{array}

Envelopment - Input Orientation, Disposable Inputs/Outputs

.. math::

   \begin{array}{rl}
   min~~ & \theta -\epsilon(\sum\limits_{i \in I_{SD}}s^- + \sum\limits_{j \in O_{SD}}s^+) \\
 st:  &\theta x_{oi} -\sum\limits_{r\in S}x_{ri}\lambda - s^-_i = 0, i \in I_{SD}\\
   &\theta x_{oi} -\sum\limits_{r \in S}x_{ri}\lambda = 0, i \in I_{WD}\\
    ~~& \sum\limits_{r\in S}y_{rj}\lambda_r - s^+_j = y_{oj}, j \in O_{SD}\\
   &\sum\limits_{r\in S} y_{rj}\lambda = y_{oj}, j \in O_{WD}\\
    &\lambda,s^+_j,s^-_i\geq 0,  r \in S, i \in I_{SD}, j \in O_{SD}.
   \end{array}

Weight Restrictions
-------------------

Weigth restrictions can be specified by directly adding constraints to the multipliers form. 
Assume there are :math:`K` weight restrictions. The :math:`k` th weight restriction constraint can be specified 
in this form

.. math::
    
    \sum\limits_{j \in O} R^O_{kj} \mu_j - \sum\limits_{i \in I} R^I_{ki} \nu_i \leq c_k, \quad k=1,2,...,K

in which :math:`R^O` and :math:`R^I` are the coefficient matrices for the weight constraints and vector :math:`c` 
specifies the difference between the weighted output minus weighted input. 

Multiplier model - input orientation with weight restrictions

.. math::

   \begin{array}{rl}
   max & \sum\limits_{j \in O} \mu_j y_{oj} \\ 
   st: & \sum\limits_{i \in I} \nu_i x_{oi}=1\\
   &\sum\limits_{i \in I} \nu_i x_{ri} + \sum\limits_{j \in O} \mu_j y_{rj}\leq 0, \quad r=1,2,...,s\\
    &-\sum\limits_{i \in I} \nu_i R_{ki} + \sum\limits_{j \in O} \mu_j R_{kj} \leq c_k, \quad k=1,2,...,K\\
   &\mu_j,\nu_i\geq \epsilon, j \in O, i \in I. 
   \end{array}

Let the dual variable corresponding to the :math:`K` weight restrictions be vector :math:`\gamma`. 
Then the envelopment form can be shown as follow:

Envelopment - input Orientation with weight restriction

.. math::

   \begin{array}{rl}
   min & \theta + \sum\limits_{k \in K} c_k \gamma_k -\epsilon(\sum\limits_{i \in I}s^- + \sum\limits_{j \in O}s^+) \\
   st: &\theta x_{oi} -\sum\limits_{r \in S} x_{ri} \lambda_r + \sum\limits_{k \in K} R^I_{ki} \gamma_k - s^-_i = 0,\text{ for } i \in I\\
    & \sum\limits_{r \in S} y_{rj}\lambda_r + \sum\limits_{k \in K} R^O_{kj} \gamma_k - s^+_j =  y_{oj},\text{ for } j \in O\\
   &\lambda_r,s^+_j,s^-_i\geq 0, r \in S, i \in I, j \in O.
   \end{array}

The following subsections show
how this general form can be used to represent absolute, virtual and price ratio constraints.

Absolute Weight Restrictions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let  :math:`R^O_{kj} = 0, j \in O, R^I_{ki} = 0,i \in I \setminus i^*, R^I_{ki^*} = 1`, then 

.. math::

    \nu_{i^*} \leq c_k

thus if :math:`c_k` is positive (negative), then the :math:`k` th weight constraint acts as an upper (a lower)
bound for input :math:`i^*`. The upper (lower) bonud for outputs can be specified in a similar manner.

Virtual Weight Restrictions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A virtual weight restriction on the :math:`i^*`\ th input is of the form [WJ90]_ :

  .. math:: \nu_{i^*}x_{oi^*} \leq c_k,

which can be specified by making :math:`R^O_{kj} = 0, j \in O, R^I_{ki} = 0,i \in I \setminus i^*, R^I_{ki^*} = x_{oi^*}`.
Note that to be feasible in DEA, :math:`c_k` must be less or equal to 1

Price Ratio Constraints
~~~~~~~~~~~~~~~~~~~~~~~

**TODO: I simply converted preice ratio contrsaints to normal contraints and applied usual restrictions as in the models above.**

When :math:`c_k = 0`, then :math:`R^O_{kj}, j\in O` and :math:`R^I_{ki}, i\in I` can be used to specify
the price ratio between the inputs and/or the outputs. 

For example, let :math:`R^O_{kj} = 0, j \in O \setminus j^*, R^O_{kj^*} = 1, R^I_{ki} = 0,i \in I \setminus i^*, R^I_{ki^*} = -q`, 
then we obtain a constraint

.. math::

     \mu_{j^*}-q\nu_{i^*} \leq 0
which specifies that the price ratio of :math:`\mu` and :math:`\nu` must not greater than :math:`q`.

Note that the ratio can be made to involve multiple inputs and/or outputs by 
putting more than one non-zero entries in :math:`R^O_{kj}, j \in O` and/or :math:`R^I_{ki},i \in I`.

Categorical Analysis
--------------------

Often, DMUs will not be directly comparable with each other (i.e. Retail stores in a built up urban area might find it easier than those in a semi-rural area). This requires users to put the DMU into categories, then rank the categories, from "least favourable" to "most favourable". 

The algorithm is as follows. DMUs with category 1 are considered first and compared  only to each other. Then DMUs with category 1 and 2 are considered, and so on. Hence, category 1 is least favourable, category 2 is more favourable and so on, for example, see [Cooper2007]_.

Two Phase
---------

When conducting DEA, it can be non-trivial to determine the value of :math:`\epsilon`. 
Alternatively, one can solve the DEA model in two phases without defining :math:`\epsilon`. 
The first phase solves a DEA model without slack variables to obtain an optimal efficiency score 
(:math:`\theta` or :math:`\phi`) and the 
second phase solves a DEA model with the efficiency score fixed and maximises the slack variables. 
The idea is demonstrated in the following input-oriented envelopment model. 

Phase 1:

.. math::

   \begin{array}{rl}
   \label{eq:env_in_phase1}
   min & \theta \\
   st: &\theta x_{oi} -\sum\limits_{r \in S} x_{ri} \lambda_r \geq 0,\text{ for } i \in I\\
    & \sum\limits_{r \in S} y_{rj}\lambda_r \geq y_{oj},\text{ for } j \in O\\
   &\lambda_r \geq 0, r \in S.
   \end{array}

By solving the phase 1 problem, we obtain the efficiency score :math:`\theta^*`. 
In phase 2, the efficiency score is fixed and the slack values are maximised.

Phase 2:

.. math::

   \begin{array}{rl}
   \label{eq:env_in_phase2}
   \max & \sum\limits_{i \in I}s^- + \sum\limits_{j \in O}s^+ \\
   st: &\theta^* x_{oi} -\sum\limits_{r \in S} x_{ri} \lambda_r - s^-_i = 0,\text{ for } i \in I\\
    & \sum\limits_{r \in S} y_{rj}\lambda_r - s^+_j =  y_{oj},\text{ for } j \in O\\
   &\lambda_r,s^+_j,s^-_i\geq 0, r \in S, i \in I, j \in O.
   \end{array}

Super Efficiency
----------------

**The algorithm that I use is very simple: go through all DMUs as usual, but before solving DEA model, remove DMU from the list of DMUs, and add it back after solving. I cannot find the reference where this algorithm come from, most likely from a book that I borrowed from Andrea or from the library.**

For a variety of reasons, super efficiency is implemented differently in the multiplier method than the envelopment method. This is obviously not preferable, and will be changed in later versions. First we define some notation. If a DMU is efficient, there are two cases: either there exists a convex combination of other DMUs that performs no worse than it (in which case the DMU is said to be "efficient but no extreme efficient"), or there exists no convex combination, in which case the DMU is said to be "Super efficient". Below we identify methods to determine which category the DMU belongs in.

In the envelopment method, super efficiency is implemented through the  scaling method outlined in [LR03]_. They use the standard scaling method given below, but their contribution is to provide a method to identify a lower bound for a scaling factor :math:`\alpha`, such that increasing :math:`\alpha` past this bound makes no difference to the results. Refer to the scaling method below.

This method is not preferred for a couple of reasons. Primarily, when weight restrictions are applied, the right hand sides of these must be scaled in non obvious ways. Secondly, when weak disposability is implemented, this scaling of inputs can result in a firm being scaled from the part of the frontier that bends backwards to a part that does not, affecting the efficiency score. Below is an alternate method, which can be found in any standard DEA textbook.


Peeling the Onion
-----------------

When a DMU is not efficient it might be interesting to investigate if it
is close to being efficient in the sense that it becomes efficient when
all currently efficient solutions are removed. Peeling the onion
refers to iteratively resolving the DEA problems and removing currently
efficient solutions after each iteration. One obtains a ranking of tiers
of DMUs, rank 1 refers to a DMU that is efficient. DMUs that become
efficient when those of rank 1 are removed are rank 2. Rank 3 DMUs are
efficient when rank 1 and 2 DMUs are removed, etc. This is described in
[BDS00]_ and [SZ03]_. The process is outlined below:

- **Input:** Set of DMUs, inputs, outputs
- **Output:** efficiency scores, peel-the-onion ranking
- #. :math:`S` = set of DMUs
  #. `CurrentRank = 1`
  #. | **While** :math:`S \neq \emptyset`
     |     Solve DEA for each of the DMUs in :math:`S` with DMU set in :math:`S`
     |     **Foreach** :math:`DMU \in S` **do**
     |         **If** `DMU` is efficient **then**
     |             Record rank of `DMU` as `CurrentRank`
     |             Remove `DMU` from :math:`S`
     |         **End**
     |      **End**
     |      `CurrentRank = CurrentRank + 1`
     | **End**


Limits on models
----------------

Some combinations of features are not yet functional. These include the following. Any of the multiplier models cannot run with two-phase.

Also, slack maximization and weight restrictions is not allowed, because
it is an unbounded problem.


References
----------

.. [Cooper2007] W. W. Cooper, L. M. Seiford and K. Tone. Data Envelopment Analysis. A Comprehensive Text with Models, Applications, References and DEA-Solver Software. Second Edition. Springer US, 492 p., 2007.

.. [CSZ04] W. W. Cooper,  L. M. Seiforda and J. ZhuJ. Handbook on data envelopment analysis. Kluwer Academic, Boston, 2004.

.. [CCLS94] A. Charnes, W. W. Cooper, A. Y. Lewin and L. M. Seiford. Data Envelopment Analysis: Theory, Methodology and Applications. Kluwer Academic Publishers Group, Dordrecht, 1994.

.. [LR03] C. A. K. Lovell and A. P. B. Rouse. Equivalent standard DEA models to provide super-efficiency scores. Journal of the Operational Research Society, 54, pp. 101-108, 2003.

.. [BDS00] R. S. Barr, M. L. Durchholz and L. Seiford. Peeling the DEA Onion: Layering and Rank-Ordering DMUs Using Tiered DEA. Southern Methodist University, Dallas, TX; i2 Technologies, Irving, TX; University of Massachusetts at Amherst, Amherst, MA, 2000.

.. [SZ03] L. M. Seiford and J. Zhu. Context-dependent data envelopment analysis -Measuring attractiveness and progress. Omega, 31, pp. 397-408, 2003.

.. [WJ90] Y.-HB. Wong and J.E. Beasley. Restricting weight flexibility in data envelopment analysis. Journal of the Operational Research Society 41-9 pp. 829-835, 1990.