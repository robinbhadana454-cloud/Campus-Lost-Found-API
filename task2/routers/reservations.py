from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from database import get_session
from models import Reservation

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.delete("/{reservation_id}", status_code=status.HTTP_200_OK)
def cancel_reservation(
    reservation_id: int,
    session: Session = Depends(get_session)
):
    """
    8. DELETE /reservations/{reservation_id}
    Cancel a reservation.
    """
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found"
        )

    session.delete(reservation)
    session.commit()
    return {"detail": f"Reservation {reservation_id} cancelled successfully"}
