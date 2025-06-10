describe('Admin Dashboard', () => {
  beforeEach(() => {
    // Mock authentication and API calls
    cy.intercept('GET', '/api/v1/admin/club/1/dashboard-summary', { fixture: 'dashboard-summary.json' }).as('getDashboardSummary');
    cy.login(); // Custom command for logging in
    cy.visit('/admin');
    cy.wait('@getDashboardSummary');
  });

  it('displays the main dashboard title', () => {
    cy.contains('h1', 'Dashboard');
  });

  it('displays the dashboard widgets with correct data', () => {
    cy.fixture('dashboard-summary.json').then((summary) => {
      cy.contains('h3', 'Today\'s Bookings').next().should('contain', summary.total_bookings_today);
      cy.contains('h3', 'Court Occupancy').next().should('contain', `${Math.round(summary.occupancy_rate_percent)}%`);
    });
  });

  it('navigates to the bookings page', () => {
    cy.get('nav').contains('Bookings').click();
    cy.url().should('include', '/admin/bookings');
  });

  it('navigates to the schedule page', () => {
    cy.get('nav').contains('Schedule').click();
    cy.url().should('include', '/admin/schedule');
  });

  it('navigates to the club profile page', () => {
    cy.get('nav').contains('Club Profile').click();
    cy.url().should('include', '/admin/club');
  });
}); 