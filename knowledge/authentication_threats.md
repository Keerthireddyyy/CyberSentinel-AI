
# Authentication Threat Investigation Knowledge

## High Authentication Volume

A large number of authentication events can indicate unusual
activity, but high volume alone does not establish maliciousness.

Possible legitimate explanations include:
- Domain controllers
- Shared authentication infrastructure
- Automated services
- Enterprise management systems

Analysts should compare activity with the computer's expected role.

## Failed Authentication Attempts

Repeated authentication failures may be associated with:
- Incorrect service account credentials
- Misconfigured applications
- Password guessing
- Credential misuse

Investigators should examine failure timing, affected users,
source computers, and authentication outcomes.

## New Network Relationships

Previously unseen computer-to-computer authentication
relationships may warrant review.

Possible explanations include:
- New software deployments
- Infrastructure changes
- Legitimate administrative activity
- Unauthorized lateral movement

A new relationship is not automatically suspicious.

## Broad User Activity

A computer associated with many user accounts may be:
- A shared server
- An authentication gateway
- A domain controller
- A system requiring further investigation

Analysts should examine the computer's operational role.

## Investigation Principles

1. Treat ML anomalies as investigative leads.
2. Do not assume unlabeled events are benign.
3. Distinguish observed evidence from hypotheses.
4. Consider legitimate operational explanations.
5. Do not declare an incident without supporting evidence.
