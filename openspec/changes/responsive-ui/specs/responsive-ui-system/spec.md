## ADDED Requirements

### Requirement: Responsive utility class
The system SHALL provide a reusable `Responsive` utility with breakpoints for phone (<600px), tablet (600-1024px), and desktop (>=1024px) based on `MediaQuery`.

#### Scenario: Responsive detects phone
- **WHEN** the screen width is less than 600px
- **THEN** `Responsive.isPhone` SHALL return true, `isTablet` SHALL return false, `isDesktop` SHALL return false

#### Scenario: Responsive detects tablet
- **WHEN** the screen width is between 600px and 1024px
- **THEN** `Responsive.isTablet` SHALL return true, `isPhone` SHALL return false, `isDesktop` SHALL return false

#### Scenario: Responsive detects desktop
- **WHEN** the screen width is 1024px or greater
- **THEN** `Responsive.isDesktop` SHALL return true, `isPhone` SHALL return false, `isTablet` SHALL return false

#### Scenario: Responsive returns different values per breakpoint
- **WHEN** calling `Responsive.value(mobile: 1, tablet: 2, desktop: 3)`
- **THEN** it SHALL return the value corresponding to the current breakpoint

### Requirement: Conditional orientation lock
The app SHALL lock to portrait orientation on phones and allow all orientations on tablets and desktop.

#### Scenario: Phone orientation lock
- **WHEN** the app starts on a device with screen width less than 600px
- **THEN** the app SHALL lock to `portraitUp` and `portraitDown` only

#### Scenario: Tablet/desktop orientation unlocked
- **WHEN** the app starts on a device with screen width 600px or greater
- **THEN** the app SHALL allow all orientations

### Requirement: Responsive HomeScreen - Stats row
The HomeScreen SHALL display stats cards in a horizontal scrollable row on phones, a 2-column grid on tablets, and a single row wrapping on desktop.

#### Scenario: Phone shows horizontal stat cards
- **WHEN** the screen width is less than 600px
- **THEN** the stats section SHALL be a horizontal `SingleChildScrollView` with fixed-width cards (current behavior)

#### Scenario: Tablet shows stat grid
- **WHEN** the screen width is between 600px and 1024px
- **THEN** the stats section SHALL display cards in a 2-column grid layout

#### Scenario: Desktop shows stat row
- **WHEN** the screen width is 1024px or greater
- **THEN** the stats section SHALL display cards in a horizontal row that wraps naturally

### Requirement: Responsive HomeScreen - Menu grid
The HomeScreen menu grid SHALL adapt its column count based on screen width: 2 columns on phones, 3 on tablets, 4 on desktop.

#### Scenario: Phone shows 2-column menu grid
- **WHEN** the screen width is less than 600px
- **THEN** the menu grid SHALL display 2 columns

#### Scenario: Tablet shows 3-column menu grid
- **WHEN** the screen width is between 600px and 1024px
- **THEN** the menu grid SHALL display 3 columns

#### Scenario: Desktop shows 4-column menu grid
- **WHEN** the screen width is 1024px or greater
- **THEN** the menu grid SHALL display 4 columns

### Requirement: Responsive LoginScreen
The LoginScreen SHALL show the form in a centered card with max width on tablets and desktop, and maintain the current full-width layout on phones.

#### Scenario: Phone shows full-width login
- **WHEN** the screen width is less than 600px
- **THEN** the login form SHALL use the current full-width layout

#### Scenario: Tablet and desktop show centered card
- **WHEN** the screen width is 600px or greater
- **THEN** the login form SHALL be displayed in a centered card with a maximum width of 400px

### Requirement: Responsive ClientesScreen
The ClientesScreen SHALL display clients as a single-column list on phones and a multi-column grid on tablets/desktop.

#### Scenario: Phone shows client list
- **WHEN** the screen width is less than 600px
- **THEN** clients SHALL be displayed as a single-column scrollable list

#### Scenario: Tablet shows 2-column client grid
- **WHEN** the screen width is between 600px and 1024px
- **THEN** clients SHALL be displayed in a 2-column grid

#### Scenario: Desktop shows 3-column client grid
- **WHEN** the screen width is 1024px or greater
- **THEN** clients SHALL be displayed in a 3-column grid

### Requirement: Responsive ProductosScreen
The ProductosScreen SHALL display products in a responsive grid.

#### Scenario: Phone shows 1-column product list
- **WHEN** the screen width is less than 600px
- **THEN** products SHALL be displayed in a single column

#### Scenario: Tablet shows 2-column product grid
- **WHEN** the screen width is between 600px and 1024px
- **THEN** products SHALL be displayed in a 2-column grid

#### Scenario: Desktop shows 3-column product grid
- **WHEN** the screen width is 1024px or greater
- **THEN** products SHALL be displayed in a 3-column grid

### Requirement: Responsive StatCard
The `StatCard` widget SHALL accept dynamic width instead of a fixed 140px, adapting to the parent constraints.

#### Scenario: StatCard fills parent width
- **WHEN** a `StatCard` is placed inside a grid or flex container
- **THEN** its width SHALL be determined by the parent constraints, not a fixed value

### Requirement: Responsive MenuCard
The `MenuCard` widget SHALL adapt its padding and icon size proportionally to the available space.

#### Scenario: MenuCard adapts to grid cell size
- **WHEN** displayed in different column counts
- **THEN** the card padding, icon container size, and font sizes SHALL scale proportionally to maintain visual balance
