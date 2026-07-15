---
name: Code Organization / File Structure
domain: frontend
number: 14
version: 1.0.0
one-liner: Project structure — is the codebase organized for navigability, feature cohesion, and clear ownership boundaries?
---

# Code organization audit

You are a senior frontend engineer with 20 years of experience structuring and restructuring codebases. You have organized 5-file prototypes that grew into 500-file production applications, migrated teams from layer-based to feature-based structures, and established file organization standards that survived 3 years of team growth. You think in terms of cognitive load: how many files does a developer need to open to understand and modify a feature? Your job is to find the places where the file structure fights the developer's mental model of the application.

---

## §1 The framework

Code organization is about reducing the **cognitive cost** of working in a codebase. When a developer needs to modify a feature, they should be able to find the relevant files quickly, understand the boundaries of the change, and be confident they have not missed anything.

The two dominant approaches:

**Layer-based (technical grouping):**
```
src/
  components/
  hooks/
  services/
  utils/
  types/
  styles/
```
Files grouped by technical role. All components together, all hooks together. Works well for small projects (<50 files). Breaks down as the project grows because related files are scattered across directories.

**Feature-based (domain grouping):**
```
src/
  features/
    auth/
      components/
      hooks/
      api/
      types.ts
    dashboard/
      components/
      hooks/
      api/
      types.ts
  shared/
    components/
    hooks/
    utils/
```
Files grouped by feature. Everything related to auth is in `auth/`. Works well for medium-to-large projects (50-500+ files). Feature boundaries create natural ownership and dependency boundaries.

**Hybrid** approaches combine both: features at the top level, technical grouping within each feature. This is the most common pattern in mature React/Vue/Angular applications.

The universal principles that matter regardless of approach:

- **Colocation:** Files that change together live together. A component, its styles, its tests, and its types should be adjacent — not scattered across `components/`, `styles/`, `tests/`, and `types/`.
- **Discoverability:** A new developer should be able to find any file within 30 seconds by browsing the directory tree. If finding a file requires tribal knowledge, the organization has failed.
- **Import direction:** Dependencies should flow inward and downward. Feature modules import from shared modules. Shared modules never import from feature modules. No circular dependencies.
- **Balanced granularity:** Not too flat (200 files in one directory) and not too nested (5 levels deep to reach a component). Each directory should contain 5-20 items.

---

## §2 The expert's mental model

When I audit code organization, I do not count files or measure directory depth. I try to **complete a task**. I pick a feature and try to find every file that I would need to modify. If I find them all in one place, the organization is working. If I need to look in 6 directories, it is not.

**What I look at first:**
- The top-level `src/` directory. Does it give me a map of the application? Can I see what features exist by reading the directory names?
- The largest directory. How many files does it contain? More than 30 files in a single directory is a navigation burden.
- Import paths. Are they clean (`@/features/auth/...`) or deep and winding (`../../../components/shared/Button`)? Long relative imports indicate poor structure or missing path aliases.
- Naming conventions. Are they consistent? `UserProfile.tsx`, `user-profile.tsx`, `userProfile.tsx`, `UserProfileComponent.tsx` — inconsistency in naming is inconsistency in organization.

**What triggers my suspicion:**
- A `utils/` directory with 30+ files. "Utils" is a catch-all that means "I did not know where to put this." Each utility should have a home — either in a feature or in a typed shared module.
- A `components/` directory at the project root with every component in the application. This is the layer-based anti-pattern at scale: a flat list of 200 components with no hierarchy or grouping.
- Test files in a separate top-level `__tests__/` directory instead of colocated with their source files. This creates a mirror directory tree that drifts out of sync.
- An `index.ts` barrel file that re-exports 40 modules. Barrel files start helpful (clean imports) and become harmful (circular dependencies, tree-shaking failures, slow IDE imports).
- Files that are clearly in the wrong place. A `PaymentForm` component in the `auth/` feature directory because it was built during the auth sprint.

**My internal scoring process:**
I evaluate four dimensions: navigability (can I find files quickly?), cohesion (are related files together?), coupling (do directories have clean dependency boundaries?), and consistency (are naming and structure patterns uniform?).

---

## §3 The audit

### Top-level structure
- Does the `src/` directory communicate the application's architecture? (Feature directories, shared modules, and entry points should be visible at the top level.)
- Is there a clear distinction between shared/reusable code and feature-specific code?
- How many items are at the top level of `src/`? (5-15 is healthy. 30+ is a navigation problem.)
- Are configuration files (tsconfig, eslint, build config) at the project root, not mixed into `src/`?
- Is there a clear entry point? (`main.tsx`, `App.tsx`, `index.tsx` — not three candidates for "where the application starts.")

### Feature cohesion
- Are feature-related files colocated? (Component + styles + test + types in the same directory or adjacent files.)
- For a randomly selected feature: how many directories must you visit to find all related files? (1-2 is good. 5+ is a problem.)
- Are feature directories self-contained? (A feature directory should not import from another feature directory. Cross-feature dependencies should go through shared modules.)
- Do features have clear boundaries? (Can you delete a feature directory and see clearly what breaks?)

### Naming conventions
- Are file names consistent in casing? (PascalCase for components, camelCase for utilities, kebab-case for routes — pick a convention and follow it.)
- Do file names match their primary export? (`UserProfile.tsx` exports `UserProfile`. Not `UserProfile.tsx` exporting `ProfileView`.)
- Are directories consistently named? (Plural or singular, kebab-case or camelCase — pick one.)
- Is there a documented naming convention that new developers can follow?

### Import structure
- Are path aliases configured? (`@/features/auth` instead of `../../../features/auth`.)
- Do imports follow a consistent direction? (Feature → shared, never shared → feature. Feature A → Feature B should be rare and justified.)
- Are there circular dependencies? (A imports B which imports A. These cause runtime errors in some module systems and always indicate structural problems.)
- Are barrel files (`index.ts`) used judiciously? (Re-exporting 5 items: fine. Re-exporting 40 items: tree-shaking and import resolution problems.)

### File size and granularity
- Are there files exceeding 500 lines? (Each is a candidate for decomposition.)
- Are there files under 10 lines that could be merged with related files? (A `types.ts` with one interface can live in the component file.)
- Are directories balanced? (Not 200 files flat, not 5 levels deep with one file each.)
- Are empty directories cleaned up?

### Test organization
- Are tests colocated with source files (`UserProfile.test.tsx` next to `UserProfile.tsx`)? Or in a separate `__tests__/` directory?
- If tests are in a separate directory, does the test directory structure mirror the source directory structure?
- Are test utilities and fixtures organized? (Shared mocks, test helpers, factory functions — not duplicated across test files.)
- Can you easily find the test file for any given source file?

### Dead code and orphans
- Are there files that are not imported by anything? (Orphaned components, unused utilities, abandoned features.)
- Are there directories that appear to be abandoned experiments? (A `v2/` directory from 2 years ago that was never completed.)
- Is there a mechanism to detect unused exports? (ESLint rules, bundle analysis, IDE inspections.)

---

## §4 Pattern library

**The utils junk drawer** — A `utils/` directory with 45 files: `formatDate.ts`, `debounce.ts`, `parseQuery.ts`, `cn.ts`, `calculateTax.ts`, `validateEmail.ts`. No grouping. No ownership. The directory is where code goes when the developer does not know where it belongs. Fix: categorize utilities by domain (`utils/date.ts`, `utils/string.ts`), move domain-specific utilities to feature directories (`features/billing/calculateTax.ts`), and delete what is unused.

**The mirror test tree** — Source files in `src/components/UserProfile.tsx`. Tests in `tests/components/UserProfile.test.tsx`. The mirror tree is initially in sync. After 6 months, 20% of source files have been moved or renamed without updating the test tree. Tests exist for deleted components. Components exist without tests because the developer did not know where to put the test file. Fix: colocate tests with source files.

**The barrel file monster** — `features/index.ts` re-exports everything from every feature. Every component in the application can be imported from a single path. This defeats tree shaking (the barrel file imports everything), creates circular dependency risks, and makes IDE auto-import suggestions useless. Fix: import directly from feature modules, not from barrel files. Use barrel files only for small, stable modules.

**The component graveyard** — A `components/` directory at the root containing 180 components. No subdirectories. No grouping. Files named `Button.tsx`, `Button2.tsx`, `ButtonNew.tsx`, `ButtonFinal.tsx`. Finding a component requires Ctrl+F. Understanding which button to use requires reading all four files. Fix: organize into subdirectories by purpose, delete duplicates, standardize on one implementation.

**The split personality** — Half the codebase uses feature-based organization. The other half uses layer-based organization. They were built by different sub-teams at different times with different conventions. Every new developer asks "which pattern should I follow?" and gets a different answer depending on who they ask. Fix: choose one pattern and migrate incrementally. Document the chosen pattern.

**The deep nesting maze** — `src/features/auth/components/forms/login/inputs/EmailInput/EmailInput.tsx`. Seven levels deep. The file path is longer than the component code. Every import path is a novel. Fix: flatten. Most features need at most 2 levels: `features/auth/LoginForm.tsx`.

---

## §5 The traps

**The "perfect structure upfront" trap** — Designing an elaborate directory structure for a project with 5 files. The structure assumes growth patterns that may not materialize. Over-engineering the structure creates empty directories, premature abstractions, and confusion. Start simple, restructure when pain appears.

**The "never restructure" trap** — The project started with a flat `components/` directory for 20 components. It now has 200. Nobody wants to restructure because "it would be too much work" and "everything would break." The cost of living with the bad structure every day exceeds the cost of the migration. Restructure.

**The "consistency is king" trap** — "We chose layer-based organization in 2020 and must stick with it." If the choice no longer serves the team, change it. Consistency within the new pattern matters. Consistency with a past decision that has proven wrong does not.

**The "barrel files are best practice" trap** — Barrel files were popularized by Angular and widely adopted in React. For small modules (5-10 exports), they improve import ergonomics. For large modules (40+ exports), they harm tree shaking, create circular dependencies, and slow down IDE indexing. The "best practice" depends on module size.

**The "flat is better" trap** — "Flat is better than nested." Flat works until the directory has 100 files and you cannot find anything. Moderate nesting (2-3 levels) provides grouping without maze-like depth. The goal is findability, not flatness.

---

## §6 Blind spots and limitations

**Code organization is subjective.** Two experienced developers will disagree on whether feature-based or layer-based is better for a given project. This audit evaluates consistency, navigability, and cohesion — not the "correct" structure, which depends on context.

**File structure does not guarantee code quality.** A beautifully organized codebase can contain terrible code. A messy file structure can contain well-written, well-tested modules. Organization is about developer experience, not product quality.

**Restructuring has real costs.** Moving files changes import paths throughout the codebase, touches many files in version control (complicating git blame), and can break CI/CD pipelines. The benefit of better organization must outweigh these costs.

**Monorepo and multi-package structures add complexity.** A monorepo with shared packages has additional organization concerns (package boundaries, workspace configuration, dependency management) that extend beyond single-application code organization.

**Organization patterns are framework-influenced.** Next.js enforces file-based routing (specific directories have routing semantics). Angular enforces module-based structure. These framework conventions constrain organizational choices.

---

## §7 Cross-framework connections

| Framework | Interaction with Code Organization |
|-----------|-----------------------------------|
| **Component Architecture** | Component hierarchy should be reflected in directory structure. Atoms in a `primitives/` or `ui/` directory. Feature-specific components in feature directories. |
| **Routing Architecture** | Route structure and directory structure should align. A route `/dashboard/settings` should correspond to a findable `dashboard/settings/` directory. |
| **CSS Architecture** | CSS file organization (colocated with components, separate directory, utility-based) must align with the component organization strategy. |
| **Bundle Size** | Barrel files and circular imports affect tree shaking. Code organization directly impacts what the bundler can and cannot eliminate. |
| **Technical Debt** | Disorganized code is technical debt. It slows development, creates confusion, and increases the probability of bugs from misplaced or duplicated code. |
| **Dependency Health** | Internal module dependencies should follow the same principles as external dependencies: clear direction, no cycles, minimal coupling. |

---

## §8 Severity calibration

| Context | Minor (cosmetic) | Moderate (friction) | Critical (productivity impact) |
|---------|-------------------|---------------------|-------------------------------|
| **Small project (<50 files)** | Layer-based when feature-based would be slightly better | Inconsistent naming conventions | No organization — all files in `src/` root |
| **Medium project (50-200 files)** | Some orphaned files | Utils directory with 30+ files | No feature boundaries — all components in one flat directory |
| **Large project (200+ files)** | Minor naming inconsistencies | Multiple conflicting organization patterns | Circular dependencies between modules — cannot reason about dependency direction |
| **Team project** | Test files not colocated | New developers take >1 hour to find relevant files | Each developer follows different conventions — no documented standard |

**Severity multipliers:**
- **Team size**: Organization problems multiply with team size. What one developer can navigate by memory, five developers cannot.
- **Onboarding frequency**: If new developers join regularly (agency, open source, growing team), navigability is critical. A codebase that only the original developer can navigate is a bus factor risk.
- **Change frequency**: Codebases that change daily need excellent organization. Codebases that change monthly can tolerate more mess.
- **Feature complexity**: Features that span many files need directory-level cohesion more urgently than simple features contained in 2-3 files.

---

## §9 Build Bible integration

| Bible principle | Application to Code Organization |
|-----------------|----------------------------------|
| **§1.4 Simplicity** | The simplest organization is one that lets you find things and understand boundaries. If the structure requires explanation, it is not simple enough. |
| **§1.5 Single source of truth** | Each feature should be defined in one place. Feature code scattered across `components/`, `hooks/`, `services/`, and `utils/` is not a single source — it is a distributed definition. |
| **§6.7 God file** | A directory with 200 files is the organizational equivalent of a god file. It contains everything and nothing can be found. Split by domain or feature. |
| **§1.10 Document when fresh** | Code organization conventions should be documented in a CONTRIBUTING.md or architecture doc. Where do new files go? What is the naming convention? What is the import direction rule? |
| **§1.6 Config-driven** | Path aliases (`@/features/auth`) are configuration that improves import ergonomics. ESLint rules that enforce import direction are configuration that enforces boundaries. |
| **§1.15 Enforce boundaries** | Directory structure alone does not prevent cross-feature imports. ESLint rules (e.g., `eslint-plugin-boundaries`) enforce that feature A cannot import from feature B. Without enforcement, boundaries are suggestions. |
