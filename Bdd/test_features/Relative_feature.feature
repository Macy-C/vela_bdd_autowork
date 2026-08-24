@@step:relative_step
Feature: Relative

    Scenario Outline: Parameter ranges and initial values follow the selected cardiac phase mode
      Given a patient is registered on the console
      And the "Step & Shoot" protocol is selected
      And the clinical sequence parameters are open on the Display Interface
      When the cardiac phase mode is set to "<cardiac_phase_mode>" on the Display Interface
      Then the initial phase value shown on the Display Interface is "<initial_phase_value>"
      And the phase range shown on the Display Interface is "<phase_range>"
      And the phase tolerance range shown on the Display Interface is "<phase_tolerance_range>"

    Examples:
        | cardiac_phase_mode | initial_phase_value | phase_range      | phase_tolerance_range |
        | Relative           | 78%                 | 35% to 85%       | 0% to 5%              |