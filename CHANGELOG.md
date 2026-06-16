# Changelog

## 0.2.0

Compatibility release — the Robolist.ai page structure changed and the
0.1.0 client no longer worked against it. This release fixes both API
methods and refreshes the docs.

### Fixed
- **`get_robot()` now finds the Product node.** Robolist moved its
  page-specific schema.org data into a top-level `@graph` block. The
  0.1.0 client only looked for a top-level `Product` type and therefore
  raised `ParseError` on every robot. The client now flattens `@graph`
  and parses the `Product` node inside it.
- **`get_company()` now returns the company, not the site.** Robolist
  added a site-wide `Organization` ("Robolist.ai") block to every page.
  The 0.1.0 client grabbed the *first* `Organization` and so returned
  the site itself with no robots. The client now matches the
  `Organization` whose `@id` points at a `/companies/` URL, and reads
  the robot list from the page's `CollectionPage → ItemList`.
- Old/merged slugs are resolved transparently; `Robot.slug` and
  `Company.slug` now reflect the canonical record after any redirect.

### Added
- `Robot.category`, `Robot.country_of_origin`, `Robot.launch_year`, and
  `Robot.date_modified` — all now published in the page JSON-LD.
- `Company.founding_date` and `Company.country`.
- `RobotSummary.position` — the robot's position in the company listing.

### Changed
- "Product Score" renamed to **Robo Index** throughout, matching the
  live site.
- `Robot.score` is now documented as best-effort: the Robo Index is not
  currently published in the page JSON-LD, so this field is usually
  `None`. Open `Robot.url` for the live value.
- README stats corrected (3,200+ robots / 1,200+ companies) and the
  category table updated with actuators, dexterous hands, and tactile
  sensors. Example slugs replaced with ones that resolve.

## 0.1.0

- Initial release.
