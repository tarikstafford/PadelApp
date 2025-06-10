describe('Booking Management', () => {
  beforeEach(() => {
    cy.intercept('GET', '/api/v1/admin/club/1/bookings*', { fixture: 'bookings-list.json' }).as('getBookings');
    cy.login();
    cy.visit('/admin/bookings');
    cy.wait('@getBookings');
  });

  it('displays the bookings data table', () => {
    cy.contains('h1', 'Bookings');
    cy.get('table').should('be.visible');
    cy.get('tbody tr').should('have.length', 2);
  });

  it('filters bookings by status', () => {
    cy.intercept('GET', '/api/v1/admin/club/1/bookings*status=CONFIRMED*', {
      body: {
        bookings: [
          {
            "id": 1,
            "start_time": "2023-10-28T10:00:00Z",
            "end_time": "2023-10-28T11:00:00Z",
            "status": "CONFIRMED",
            "court": { "id": 1, "name": "Court 1" },
            "user": { "id": 101, "name": "John Doe" }
          }
        ],
        pageCount: 1
      }
    }).as('getConfirmedBookings');

    cy.get('[data-testid=status-filter] button').click();
    cy.get('[data-testid=status-filter]').contains('Confirmed').click();
    cy.wait('@getConfirmedBookings');
    cy.get('tbody tr').should('have.length', 1);
    cy.get('tbody tr').first().should('contain', 'CONFIRMED');
  });

  it('views booking details', () => {
    cy.intercept('GET', '/api/v1/admin/bookings/1/game', { fixture: 'game-details.json' }).as('getGameDetails');
    cy.get('tbody tr').first().contains('button', 'View').click();
    cy.wait('@getGameDetails');
    cy.get('[data-testid=booking-details-dialog]').should('be.visible');
  });
}); 