This page provides a complete reference of all supported functions for custom calculations in AI/BI dashboards. For information about how to use custom calculations, see [What are custom calculations?](/aws/en/dashboards/manage/data-modeling/custom-calculations/).

## Aggregate functions

All calculated measures must be aggregated. The following aggregation operations are supported:

note

Use the `DISTINCT` keyword in aggregate functions to include only unique values in the aggregation. Additionally, the `FILTER(WHERE condition)` clause can be appended to any aggregate function to limit the values that are included in the calculation.

Aggregate functions can also be used with window function syntax (OVER clause) or AGGREGATE OVER syntax to create [level of detail expressions](/aws/en/dashboards/manage/data-modeling/custom-calculations/level-of-detail).

| Function | Description |
| --- | --- |
| [any(expr)](/aws/en/sql/language-manual/functions/any) | Returns `true` if at least one value of `expr` in the group is `true`. |
| [any\_value(expr)](/aws/en/sql/language-manual/functions/any_value) | Returns some value of `expr` for a group of rows. |
| [approx\_count\_distinct(expr[, relativeSD])](/aws/en/sql/language-manual/functions/approx_count_distinct) | Returns the estimated number of distinct values in `expr`. |
| [approx\_percentile ([ALL | DISTINCT] expr, percentile [, accuracy])](/aws/en/sql/language-manual/functions/approx_percentile) | Returns the approximate percentile value of `expr` at the specified percentile. |
| [avg(expr)](/aws/en/sql/language-manual/functions/avg) | Returns the calculated mean in a column or expression. |
| [bool\_or(expr)](/aws/en/sql/language-manual/functions/bool_or) | Returns `true` if at least one value of `expr` is `true`. |
| [corr(expr1, expr2)](/aws/en/sql/language-manual/functions/corr) | Returns the Pearson correlation coefficient between `expr1` and `expr2`. |
| [count(\*)](/aws/en/sql/language-manual/functions/count) | Returns the number of rows in a group. |
| [count(DISTINCT expr)](/aws/en/sql/language-manual/functions/count) | Returns the number of unique rows in a group. |
| [count\_if(expr)](/aws/en/sql/language-manual/functions/count_if) | Returns the count of rows that satisfy a given condition. |
| [first(expr [, ignoreNull])](/aws/en/sql/language-manual/functions/first) | Returns the first value of `expr` for a group. |
| [first\_value(expr [, ignoreNull])](/aws/en/sql/language-manual/functions/first_value) | Returns the first value of `expr` for a group. |
| [last(expr [, ignoreNull])](/aws/en/sql/language-manual/functions/last) | Returns the last value of `expr` for the group. |
| [last\_value(expr [, ignoreNull])](/aws/en/sql/language-manual/functions/last_value) | Returns the last value of `expr` for the group. |
| [listagg(expr [, delimiter])](/aws/en/sql/language-manual/functions/listagg) | Returns the concatenation of non-null values in the group. |
| [max(expr)](/aws/en/sql/language-manual/functions/max) | Returns the maximum value in a column or expression. |
| [max\_by(expr1, expr2)](/aws/en/sql/language-manual/functions/max_by) | Returns the value of `expr1` associated with the maximum value of `expr2`. |
| [mean(expr)](/aws/en/sql/language-manual/functions/mean) | Returns the calculated mean in a column or expression. |
| [median(expr)](/aws/en/sql/language-manual/functions/median) | Returns the median of a set of values. |
| [min(expr)](/aws/en/sql/language-manual/functions/min) | Returns the minimum value in a column or expression. |
| [min\_by(expr1, expr2)](/aws/en/sql/language-manual/functions/min_by) | Returns the value of `expr1` associated with the minimum value of `expr2`. |
| [mode(expr [, deterministic ])](/aws/en/sql/language-manual/functions/mode) | Returns the most frequent value for `expr`. |
| [percentile(expr, percentage [, frequency])](/aws/en/sql/language-manual/functions/percentile) | Returns the exact percentile value of `expr` at the specified percentile in a group. |
| [percentile\_approx(expr, percentage [, accuracy])](/aws/en/sql/language-manual/functions/percentile_approx) | Returns the approximate percentile value of `expr` at the specified percentile. |
| [regr\_slope(y, x)](/aws/en/sql/language-manual/functions/regr_slope) | Returns the slope of the linear regression line for non-null pairs in a group. |
| [some(expr)](/aws/en/sql/language-manual/functions/some) | Returns `true` if at least one value of `expr` in the group is `true`. |
| [std(expr)](/aws/en/sql/language-manual/functions/std) | Returns the standard deviation of a set of values. |
| [stddev(expr)](/aws/en/sql/language-manual/functions/stddev) | Returns the standard deviation of a set of values. |
| [stddev\_pop(expr)](/aws/en/sql/language-manual/functions/stddev_pop) | Returns the population standard deviation of a set of values. |
| [stddev\_samp(expr)](/aws/en/sql/language-manual/functions/stddev_samp) | Returns the sample standard deviation of a set of values. |
| [string\_agg(expr [, delimiter])](/aws/en/sql/language-manual/functions/string_agg) | Returns the concatenation of non-null string values in the group. |
| [sum(expr)](/aws/en/sql/language-manual/functions/sum) | Returns the total of values in a column or expression. |
| [variance(expr)](/aws/en/sql/language-manual/functions/variance) | Returns the variance of a set of values. |

## Window functions

Scalar window functions, native to SQL, perform calculations across a set of rows that are related to the current row. In addition to [aggregate functions](#aggregate-functions), scalar window functions can be used with ranking and analytic functions. For detailed syntax and usage, see [Window functions](/aws/en/sql/language-manual/sql-ref-window-functions).

### Ranking window functions

All ranking window functions are supported in custom calculations. These functions assign ranks or positions to rows within a partition. For complete syntax and examples, see [ranking window functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#ranking-window-functions).

| Function | Description |
| --- | --- |
| [dense\_rank()](/aws/en/sql/language-manual/functions/dense_rank) | Returns the rank of a value compared to all values in the partition. |
| [ntile(n)](/aws/en/sql/language-manual/functions/ntile) | Divides the rows for each window partition into n buckets ranging from 1 to at most `n`. |
| [percent\_rank()](/aws/en/sql/language-manual/functions/percent_rank) | Computes the percentage ranking of a value within the partition. |
| [rank()](/aws/en/sql/language-manual/functions/rank) | Returns the rank of a value compared to all values in the partition. |
| [row\_number()](/aws/en/sql/language-manual/functions/row_number) | Assigns a unique, sequential number to each row, starting with one, according to the ordering of rows within the window partition. |

### Analytic window functions

All analytic window functions are supported in custom calculations. These functions access values from other rows in the window. For complete syntax and examples, see [analytic window functions](/aws/en/sql/language-manual/sql-ref-functions-builtin#analytic-window-functions).

| Function | Description |
| --- | --- |
| [cume\_dist()](/aws/en/sql/language-manual/functions/cume_dist) | Returns the position of a value relative to all values in the partition. |
| [lag(expr [, offset [, default]])](/aws/en/sql/language-manual/functions/lag) | Returns the value of `expr` from a preceding row within the partition. |
| [lead(expr [, offset [, default]])](/aws/en/sql/language-manual/functions/lead) | Returns the value of `expr` from a subsequent row within the partition. |
| [nth\_value(expr, offset [, ignoreNulls])](/aws/en/sql/language-manual/functions/nth_value) | Returns the value of `expr` at a specific `offset` in the window. |

## Arithmetic operations

You can combine expressions with the following arithmetic operations:

| Operation | Description |
| --- | --- |
| [expr1 % expr2](/aws/en/sql/language-manual/functions/percentsign) | Returns the remainder of dividing `expr1` by `expr2`. |
| [multiplier \* multiplicand](/aws/en/sql/language-manual/functions/asterisksign) | Returns the product of two expressions. |
| [expr1 + expr2](/aws/en/sql/language-manual/functions/plussign) | Returns the sum of `expr1` and `expr2`. |
| [+ expr](/aws/en/sql/language-manual/functions/plussignunary) | Returns the value of the expression. |
| [expr1 - expr2](/aws/en/sql/language-manual/functions/minussign) | Returns the difference when subtracting `expr2` from `expr1`. |
| [- expr](/aws/en/sql/language-manual/functions/minussignunary) | Returns the negated value of the expression. |
| [dividend / divisor](/aws/en/sql/language-manual/functions/slashsign) | Returns the result of dividing the dividend by the divisor. |
| [dividend div divisor](/aws/en/sql/language-manual/functions/div) | Returns the integral part of the division of `dividend` by `divisor`. |
| [abs(expr)](/aws/en/sql/language-manual/functions/abs) | Returns the absolute value of the numeric expression. |
| [acos(expr)](/aws/en/sql/language-manual/functions/acos) | Returns the inverse cosine (arc cosine) of `expr`. |
| [asin(expr)](/aws/en/sql/language-manual/functions/asin) | Returns the inverse sine (arc sine) of `expr`. |
| [bround(expr [, d])](/aws/en/sql/language-manual/functions/bround) | Returns `expr` rounded to `d` decimal places using HALF\_EVEN rounding mode. |
| [ceil(expr) or ceiling(expr)](/aws/en/sql/language-manual/functions/ceil) | Returns the smallest integer not smaller than `expr`. |
| [cos(expr)](/aws/en/sql/language-manual/functions/cos) | Returns the cosine of `expr`. |
| [exp(expr)](/aws/en/sql/language-manual/functions/exp) | Returns e raised to the power of `expr`. |
| [floor(expr)](/aws/en/sql/language-manual/functions/floor) | Returns the largest integer not greater than `expr`. |
| [ln(expr)](/aws/en/sql/language-manual/functions/ln) | Returns the natural logarithm of the expression. |
| [log(base, expr)](/aws/en/sql/language-manual/functions/log) | Returns the logarithm of `expr` with the specified `base`. |
| [log10(expr)](/aws/en/sql/language-manual/functions/log10) | Returns the base-10 logarithm of the expression. |
| [mod(expr1, expr2)](/aws/en/sql/language-manual/functions/mod) | Returns the remainder of dividing `expr1` by `expr2`. |
| [nullifzero(expr)](/aws/en/sql/language-manual/functions/nullifzero) | Returns `NULL` if `expr` is 0, otherwise returns `expr`. |
| [pi()](/aws/en/sql/language-manual/functions/pi) | Returns the value of pi. |
| [pmod(expr1, expr2)](/aws/en/sql/language-manual/functions/pmod) | Returns the positive value of `expr1` mod `expr2`. |
| [pow(expr1, expr2) or power(expr1, expr2)](/aws/en/sql/language-manual/functions/power) | Returns the result of `expr1` raised to the power of `expr2`. |
| [radians(expr)](/aws/en/sql/language-manual/functions/radians) | Converts degrees to radians. |
| [rand([seed])](/aws/en/sql/language-manual/functions/rand) | Returns a random value with uniform distribution in the range from 0 (inclusive) to 1 (exclusive). |
| [round(expr [, d])](/aws/en/sql/language-manual/functions/round) | Returns `expr` rounded to `d` decimal places using HALF\_UP rounding mode. |
| [sign(expr)](/aws/en/sql/language-manual/functions/sign) | Returns the sign of the numeric expression. |
| [sin(expr)](/aws/en/sql/language-manual/functions/sin) | Returns the sine of `expr`. |
| [sqrt(expr)](/aws/en/sql/language-manual/functions/sqrt) | Returns the square root of `expr`. |
| [try\_add(expr1, expr2)](/aws/en/sql/language-manual/functions/try_add) | Adds two values. If an error occurs, returns `NULL`. |
| [try\_divide(dividend, divisor)](/aws/en/sql/language-manual/functions/try_divide) | Divides the dividend by the divisor. If an error occurs, returns `NULL`. |
| [try\_multiply(multiplier, multiplicand)](/aws/en/sql/language-manual/functions/try_multiply) | Multiplies two numbers. If an error occurs, returns `NULL`. |
| [try\_subtract(expr1, expr2)](/aws/en/sql/language-manual/functions/try_subtract) | Subtracts `expr2` from `expr1`. If an error occurs, returns `NULL`. |
| [zeroifnull(expr)](/aws/en/sql/language-manual/functions/zeroifnull) | Returns 0 if `expr` is `NULL`, otherwise returns `expr`. |

## Boolean functions and operators

Custom calculations support basic comparison and Boolean operators. The following operators and functions are supported:

| Operation | Description |
| --- | --- |
| [expr1 != expr2](/aws/en/sql/language-manual/functions/bangeqsign) | Returns `true` if `expr1` is not equal to `expr2`. |
| [!expr](/aws/en/sql/language-manual/functions/not) | Logical not. |
| [expr1 & expr2](/aws/en/sql/language-manual/functions/bit_and) | Returns the bitwise AND of `expr1` and `expr2`. |
| [expr1 && expr2](/aws/en/sql/language-manual/functions/and) | Returns `true` if both `expr1` and `expr2` are `true`. |
| [expr1 <=> expr2](/aws/en/sql/language-manual/functions/lteqgtsign) | Returns same result as the equal operator for non-null operands, but returns `true` if both are `null`, and `false` if one is `null`. |
| [expr1 <> expr2](/aws/en/sql/language-manual/functions/ltgtsign) | Returns `true` if `expr1` is not equal to `expr2`. |
| [expr1 < expr2](/aws/en/sql/language-manual/functions/ltsign) | Returns `true` if `expr1` is less than `expr2`. |
| [expr1 <= expr2](/aws/en/sql/language-manual/functions/lteqsign) | Returns `true` if `expr1` is less than or equal to `expr2`. |
| [expr1 = expr2](/aws/en/sql/language-manual/functions/eqsign) | Returns `true` if `expr1` equals `expr2`. |
| [expr1 == expr2](/aws/en/sql/language-manual/functions/eqeqsign) | Returns `true` if `expr1` equals `expr2`. |
| [expr1 > expr2](/aws/en/sql/language-manual/functions/gtsign) | Returns `true` if `expr1` is greater than `expr2`. |
| [expr1 >= expr2](/aws/en/sql/language-manual/functions/gteqsign) | Returns `true` if `expr1` is gr