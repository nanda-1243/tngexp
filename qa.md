I understand. You need comprehensive QA testing starting from admin login, testing every button and feature systematically across all four roles (admin, doctor, reception, patient). Here's the exhaustive testing plan:

## Comprehensive QA Testing Plan

**Phase 1: Admin Login & Admin-Only Features**
1. Login as admin (nanda/Password@123)
2. Dashboard: verify all widgets load (stats, queue, recent activity)
3. User Management: add user, edit user, delete user, change roles, verify permissions cascade
4. Catalog (Medicines): add, edit, delete, search, filter by category
5. Catalog (Dosages, Durations, Diagnoses, Suggestions): same add/edit/delete flow
6. Settings (Languages): add/edit/delete language, verify display in patient portal
7. Reports: view all report types, verify metrics accuracy, export functionality
8. Portal Approvals: view pending family links, approve/deny, verify state transitions
9. Queue Management: bulk status changes, batch actions
10. Check command palette (⌘K) on admin pages - verify all actions are registered

**Phase 2: Doctor Login & Doctor-Scoped Features**
1. Login as doctor (akhila/Password@123)
2. Live Queue: view only patients checked in by reception today, not admin's registered list
3. Consultation: start consultation, add medicines/diagnoses/suggestions, verify 8-medicine limit
4. Consultation save: set revisit_date, verify proper follow-up dedup
5. Follow-ups: view ONLY own follow-ups (not all doctors' follow-ups)
6. Rx Preview: view, edit, export PDF
7. VC (Virtual Consultations): start call, compose message (no Patient role toggle visible), voice console
8. Sidebar: verify only doctor-scoped pages visible (not Settings, not User Management)
9. Try accessing admin pages directly (Settings, Reports) - should be blocked
10. Check ⌘K palette - doctor-specific actions only

**Phase 3: Reception Login & Reception-Scoped Features**
1. Login as reception (priya/Password@123)
2. Register Patient: full flow with all fields, duplicate detection
3. Check-in Patient: live queue updates, arrival tracking
4. Visit Slips: generate detail slip (with recent meds/suggestions), print
5. Status Board: view all branch patients grouped by status
6. Appointments: view scheduled appointments, verify column headers match data
7. Follow-ups: view ALL upcoming revisits (all doctors), not filtered
8. Try to start consultation - should be blocked/hidden
9. Try accessing Settings, Reports - should be blocked
10. Verify only reception sidebar items visible

**Phase 4: Patient Login & Portal Features (mobile 390×844 + desktop 1440×900)**
1. Login as patient (ravali/NewPass@1234 or default fallback)
2. Forced password change: verify modal, set new password, auto-login after
3. Home dashboard: view consultations, appointments, pending approvals
4. Chat: send message to doctor, verify delivery/read ticks, attachments, emoji support
5. Prescription detail: view medicines, dosages, suggestions, export PDF
6. Book appointment: select visit type, choose date, confirm booking
7. Family linking: initiate link request, verify pending state, approve from peer, verify admin approval tab, access shared Rx
8. Profile edit: update phone/email, request name change (admin approval flow)
9. Sidebar: verify only portal-scoped pages visible
10. Try accessing staff pages (/doctor, /admin, /reception) - should redirect to portal
11. Test mobile responsiveness: layout reflow, touch targets, viewport behavior
12. Breadcrumb titles on all pages - verify correct section labels

**Phase 5: Cross-Role Access Control Tests**
1. Doctor login → try accessing admin Settings - verify 403 or redirect
2. Admin login → try accessing doctor Consultation workspace - verify 403 or appropriate gate
3. Reception login → try accessing doctor Follow-ups page - verify filtered/blocked
4. Patient login → try accessing staff sidebar items - verify blocked
5. Logout patient, login as doctor → verify patient portal inaccessible, staff pages accessible
6. Test permission-denied error states: verify only `loc`/`msg`/`type` fields in 422 responses (no request body echo)

**Phase 6: Edge Cases & Error States**
1. Consultation with no medicines - verify error or allow
2. Follow-up revisit_date before today - verify validation
3. Family link approval from non-member - verify permission denied
4. Appointment booking with no available slots - verify error message
5. Chat attachment exceeding 4MB - verify rejection
6. Portal upload quota exceeded (100MB) - verify graceful failure
7. Duplicate patient registration - verify detection logic
8. Check-in already-checked-in patient - verify idempotence or error

**Phase 7: Button Presence & Visibility Matrix**
Create a checklist for each page of which role should see which button:
- Register Patient button: reception ✓, doctor ✗, admin ✗, patient ✗
- Edit Consultation button: doctor ✓ (own only), admin ✓, reception ✗, patient ✗
- Approve Family Link: admin ✓, others ✗
- Book Appointment: patient ✓ (own), others ✗
- etc. for all ~30 buttons across all pages

**Phase 8: Screenshot Capture for Each Major Flow**
- Admin user management
- Doctor consultation with follow-up
- Reception check-in and slip generation
- Patient portal complete journey (mobile + desktop)
- All error states and permission denials

After completing this systematic testing, document:
1. Which buttons/features work as expected
2. All bugs found (with screenshot evidence)
3. Which cross-role access control works vs. fails
4. Which edge cases are handled vs. crash

This ensures complete coverage with no overlooks.