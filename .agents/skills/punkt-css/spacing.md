# Spacing

## Utility class format

`{type}{direction}-{size}` with optional `--{breakpoint}-up` for responsive spacing.

### Type

| Prefix | Property |
| ------ | -------- |
| `m`    | margin   |
| `p`    | padding  |
| `gap`  | gap      |

### Direction

| Suffix   | Sides        |
| -------- | ------------ |
| `t`      | top          |
| `r`      | right        |
| `b`      | bottom       |
| `l`      | left         |
| `x`      | left + right |
| `y`      | top + bottom |
| _(none)_ | all sides    |

### Recommended sizes

These are the documented spacing scale values. Use these in new code.

| Token      | Value    | Pixels |
| ---------- | -------- | ------ |
| `size-0`   | 0        | 0      |
| `size-2`   | 0.125rem | 2px    |
| `size-4`   | 0.25rem  | 4px    |
| `size-8`   | 0.5rem   | 8px    |
| `size-12`  | 0.75rem  | 12px   |
| `size-16`  | 1rem     | 16px   |
| `size-24`  | 1.5rem   | 24px   |
| `size-32`  | 2rem     | 32px   |
| `size-40`  | 2.5rem   | 40px   |
| `size-64`  | 4rem     | 64px   |
| `size-104` | 6.5rem   | 104px  |

### Available but not recommended

These sizes exist in the CSS but are not part of the documented spacing scale. They can be used when needed but prefer the recommended sizes.

| Token      | Value    | Pixels |
| ---------- | -------- | ------ |
| `size-6`   | 0.375rem | 6px    |
| `size-48`  | 3rem     | 48px   |
| `size-52`  | 3.25rem  | 52px   |
| `size-56`  | 3.5rem   | 56px   |
| `size-72`  | 4.5rem   | 72px   |
| `size-80`  | 5rem     | 80px   |
| `size-88`  | 5.5rem   | 88px   |
| `size-128` | 8rem     | 128px  |

### Deprecated sizes

Do not use in new code. These exist for backwards compatibility only.

`size-5`, `size-10`, `size-15`, `size-20`, `size-30`, `size-50`, `size-60`, `size-75`, `size-100`

## Examples

```html
<!-- Margin bottom 24px -->
<p class="mb-size-24">Paragraph with bottom margin</p>

<!-- Padding on all sides 16px -->
<div class="p-size-16">Padded box</div>

<!-- Horizontal padding 12px -->
<div class="px-size-12">Left and right padding</div>

<!-- Vertical margin 32px -->
<section class="my-size-32">Section with top and bottom margin</section>

<!-- Reset margin right to 0 -->
<div class="mr-size-0">No right margin</div>

<!-- Gap for flex/grid containers -->
<div class="gap-size-16" style="display: flex;">...</div>
```

## Responsive spacing

Add `--{breakpoint}-up` to apply spacing at a breakpoint and above:

```html
<!-- 16px bottom margin on mobile, 32px from tablet up -->
<p class="mb-size-16 mb-size-32--tablet-up">Responsive margin</p>

<!-- 12px horizontal padding on mobile, 24px from laptop up -->
<div class="px-size-12 px-size-24--laptop-up">Responsive padding</div>

<!-- No padding on mobile, 32px from tablet up -->
<div class="p-size-0 p-size-32--tablet-up">Progressive padding</div>
```

## SCSS usage

> Requires SCSS embedding method.

```scss
@use 'sass:map';
@use '@oslokommune/punkt-css/dist/scss/abstracts/variables';

.my-element {
  padding: map.get(variables.$spacing, 'size-24');
  margin-bottom: map.get(variables.$spacing, 'size-16');
}
```
