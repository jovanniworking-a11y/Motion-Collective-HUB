# ml01 · Predict turnout from RSVPs
After a few events you'll have pairs: (RSVP heads a week before, people who actually came). A straight line through those
points lets you predict the next night. That's "training a model" in its simplest form.

Fill in `exercise.py`, no libraries beyond NumPy:
1. `fit(x, y)`: find `a, b` so that `y ≈ a*x + b` (least squares: `a = cov(x, y) / var(x)`, `b = mean(y) - a*mean(x)`).
2. `predict(a, b, x)`.
3. `r2(y, y_pred)`: how good the fit is (1 - sum of squared errors / total variance). 1.0 is perfect.

The data in `check.py` is synthetic: about 1.4 people come per RSVP head, plus 5 walk-ins.
