# ⭐ Bonus: predict no-shows · 200 XP
If the clinic knew which bookings are likely to be missed, it could call those patients or double-book carefully.
That's a **classifier**: input facts about a booking, output a probability of a no-show.

Two facts per booking: `lead_days` (how far ahead it was booked) and `past_no_shows` (that patient's history).
The check generates synthetic history where both raise the risk.

Write logistic regression **from scratch** with NumPy in `quest.py`:
1. `sigmoid(z)` = 1 / (1 + e^-z)
2. `train(X, y, lr=0.1, steps=2000)`: standardise each column (subtract the mean, divide by the std, and remember both),
   then gradient descent on the weights `w` and bias `b`. Return a model dict `{"w", "b", "mean", "std"}`.
3. `predict_proba(model, X)` and `predict(model, X)` (probability ≥ 0.5 → 1).

To pass: at least 75% accuracy on unseen bookings, and better than always guessing "shows up".

<details><summary>Hint</summary>

Each step: `p = sigmoid(Xs @ w + b)`; `w -= lr * Xs.T @ (p - y) / n`; `b -= lr * (p - y).mean()`.
</details>
