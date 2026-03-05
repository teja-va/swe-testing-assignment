# Testing Strategy

## Testing Strategy

The main goal of the testing overall and in this task is to ensure that everything works correctly according to the requiremnts. It is devided into two parts: unit testing(calculation logic) and integration testing(intaraction of UI with logic)


# What Was Tested

## Unit Tests

Unit tests were written for the calculation logic. These tests verify the behavior of individual functions in isolation.

The following was tested:
- Addition
- Subtraction
- Multiplication
- Division
- Division by zero
- Negative number calculations
- Decimal numbers
- Very large numbers
- Invalid numeric input

Passing theese test mean that calculation orecation works correctly for normal and edge cases


## Integration Tests

Integration tests checks whether different components work correctly together. For this task it is simulation of real intaraction with UI.

The following was tested:
- Performing addition using button presses
- Performing multi-digit addition
- Resetting the calculator using the Clear button
- Handling division by zero in the UI
- Using decimal numbers in calculations

These tests confirm that the UI correctly communicates with calculation logic.



# What Was Not Tested

Some aspects were not tested because they are not important for the task:

- Visual appearance of the UI
- Accessibility testing
- etc.



# Lecture Concepts Used

## Testing Pyramid

The testing approach follows the testing pyramid model.  
9 are unit tests because they are fast and isolated. 5 integration tests verify how the UI interacts with the logic layer. It allows to check core functionlity quickly and verify user workflow with the smaller amount of tests

## Black-Box vs White-Box Testing

Two different testing approaches were used: Wite-box for unit tests. They check all calculation directly the result and inpet are defined and can be checked manualy; black-box for integration tests. They are checking workflows without direct information about internal processes.

## Functional vs Non-Functional Testing

Tests for this project are all about fuctional testing. All of them are verifing correctness of outputs for given inputs. Non-functional testing was not included because it is not required by the task.

## Regression Testing

For this task regression testing is ability to check whether everything works correctly with pytest comment in any moment of the development. If something new added to the project, it helps to make sure that nothing has been broken.
# Test Results Summary

| Test Name | Test Type | Status |
|----------|-----------|--------|
| test_add | Unit | Pass |
| test_sub | Unit | Pass |
| test_mul | Unit | Pass |
| test_div | Unit | Pass |
| test_div_by_zero | Unit | Pass |
| test_negative_numbers | Unit | Pass |
| test_decimal_numbers_from_strings | Unit | Pass |
| test_very_large_numbers | Unit | Pass |
| test_to_decimal_rejects_bad_string | Unit | Pass |
| test_addition_5_plus_3_equals_8 | Integration | Pass |
| test_addition_10_plus_3_equals_13 | Integration | Pass |
| test_ui_clear | Integration | Pass |
| test_ui_division_by_zero_shows_error | Integration | Pass |
| test_ui_decimal_input_1_point_5_times_2_equals_3 | Integration | Pass |