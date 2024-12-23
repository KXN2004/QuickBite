import logging

from fastapi import APIRouter, Depends, HTTPException, Header, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from controller.token import verify_access_token
from models.Cart import Cart
from models.Cart import validate_cart_items, get_order_details, verify_payment
from models.Orders import Payments, Orders

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/user/api",
)


class Payment(BaseModel):
    payment_id: str
    payment_signature: str


def logger_object():
    """Function to create a logger object to log the backend to the console"""
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


log = logger_object()


class CartItem(BaseModel):
    item_id: int


# Dependency to check for a valid JWT token in the header
def check_jwt_token(authorization: str = Header(..., description="JWT token")):
    token_prefix, token = authorization.split()
    if token_prefix.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type. Use Bearer authentication.",
        )
    return verify_access_token(token)


@router.get('/', dependencies=[Depends(check_jwt_token)])
def check_connection(decoded_token: dict = Depends(check_jwt_token)):
    print(decoded_token)
    """To check connection"""
    print("Checking successful")
    return "Checking successful"


@router.get('/menu', dependencies=[Depends(check_jwt_token)])
def menu():
    """To check connection"""
    print("Checking successful")
    return {"message": "Menu"}


@router.get('/cart', dependencies=[Depends(check_jwt_token)])
def get_cart(user_data=Depends(check_jwt_token)):
    """
    This endpoint retrieves the user's cart.

    It uses the HTTP GET method and is located at the path '/cart'.

    This function is dependent on the check_jwt_token function, which verifies the JWT token in the request header.

    Parameters:
    user_data (dict): User data obtained from the JWT token. It is expected to contain the user's ID.

    Returns:
    JSONResponse: A JSON response indicating the status of the operation. If successful, it returns a status code of 200 and the content of the user's cart.
    If an error occurs, it returns a status code of 400 and a message detailing the error.

    Raises:
    HTTPException: If an error occurs during the operation, an HTTPException is raised with a status code of 400 and a detail message containing the error.
    """
    user_id = user_data['uid']
    log.info(f"User: {user_id} requested to view their cart")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=sorted(Cart(user_id).get_cart(), key=lambda x: x['id'])
    )


@router.post('/cart/add/{item}', dependencies=[Depends(check_jwt_token)])
def add_item(item: str, user_data=Depends(check_jwt_token)):
    """
    This endpoint adds an item to the user's cart.

    It uses the HTTP POST method and is located at the path '/cart/add/{item}'.
    The item parameter in the path is an integer representing the ID of the item to be added.

    This function is dependent on the check_jwt_token function, which verifies the JWT token in the request header.

    Parameters:
    item (int): The ID of the item to be added to the cart.
    user_data (dict): User data obtained from the JWT token. It is expected to contain the user's ID.

    Returns:
    JSONResponse: A JSON response indicating the status of the operation. If successful, it returns a status code of 200 and a message indicating the item has been added and the available quantity of the item.
    If an error occurs, it returns a status code of 400 and a message detailing the error.

    Raises:
    HTTPException: If an error occurs during the operation, an HTTPException is raised with a status code of 400 and a detail message containing the error.
    """
    user_id = user_data['uid']
    log.info(f"User: {user_id} has requested to add item: {item} to their cart")
    try:
        Cart(user_id).add_item(item)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Added item to cart",
                "available quantity": Cart(user_id).item_exists(item).quantity
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post('/cart/remove/{item}', dependencies=[Depends(check_jwt_token)])
def remove_item(item: str, user_data=Depends(check_jwt_token)):
    """
    This endpoint removes an item from the user's cart.

    It uses the HTTP POST method and is located at the path '/cart/remove/{item}'.
    The item parameter in the path is an integer representing the ID of the item to be removed.

    This function is dependent on the check_jwt_token function, which verifies the JWT token in the request header.

    Parameters:
    item (int): The ID of the item to be removed from the cart.
    user_data (dict): User data obtained from the JWT token. It is expected to contain the user's ID.

    Returns:
    JSONResponse: A JSON response indicating the status of the operation. If successful, it returns a status code of 200 and a message indicating the item has been removed and the available quantity of the item.
    If an error occurs, it returns a status code of 400 and a message detailing the error.

    Raises:
    HTTPException: If an error occurs during the operation, an HTTPException is raised with a status code of 400 and a detail message containing the error.
    """
    user_id = user_data['uid']
    log.info(f"User: {user_id} has requested to remove item: {item} from their cart")
    try:
        Cart(user_id).remove_item(item)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Removed item from cart",
                "available quantity": Cart(user_id).item_exists(item).quantity
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete('/cart/delete/{item}', dependencies=[Depends(check_jwt_token)])
def delete_item(item: str, user_data=Depends(check_jwt_token)):
    """
    This endpoint deletes an item from the user's cart.

    It uses the HTTP DELETE method and is located at the path '/cart/delete/{item}'.
    The item parameter in the path is an integer representing the ID of the item to be deleted.

    This function is dependent on the check_jwt_token function, which verifies the JWT token in the request header.

    Parameters:
    item (int): The ID of the item to be deleted from the cart.
    user_data (dict): User data obtained from the JWT token. It is expected to contain the user's ID.

    Returns:
    JSONResponse: A JSON response indicating the status of the operation. If successful, it returns a status code of 200 and a message indicating the item has been deleted.
    If an error occurs, it returns a status code of 400 and a message detailing the error.

    Raises:
    HTTPException: If an error occurs during the operation, an HTTPException is raised with a status code of 400 and a detail message containing the error.
    """
    user_id = user_data['uid']
    log.info(f"User: {user_id} has requested to delete item: {item} from their cart")
    try:
        Cart(user_id).delete_item(item)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Deleted item from cart"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post('/cart/checkout', dependencies=[Depends(check_jwt_token)])
def checkout(user_data=Depends(check_jwt_token)):
    """
    This endpoint pays for the user's cart.

    It uses the HTTP GET method and is located at the path '/cart/pay'.

    This function is dependent on the check_jwt_token function, which verifies the JWT token in the request header.

    Parameters:
    user_data (dict): User data obtained from the JWT token. It is expected to contain the user's ID.

    Returns:
    JSONResponse: A JSON response indicating the status of the operation. If successful, it returns a status code of 200 and a message indicating the order has been placed.
    If an error occurs, it returns a status code of 400 and a message detailing the error.

    Raises:
    HTTPException: If an error occurs during the operation, an HTTPException is raised with a status code of 400 and a detail message containing the error.
    """
    user_id = user_data['uid']
    log.info(f"User: {user_id} has tried to checkout")
    items_requiring_modification: list = validate_cart_items(user_id)
    if items_requiring_modification:  # If there are items which require changes
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cart contains items which are unavailable in menu",
                "items": items_requiring_modification
            }
        )
    else:  # If there are no items which require modifications in their quantity
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=Cart(user_id).pay()["id"]
        )


@router.get('/cart/checkout/{order_id}')
def checkout(request: Request, order_id: str):
    order = get_order_details(order_id)
    return templates.TemplateResponse("checkout.html", {"request": request, "order": order})


@router.get("/verify_payment")
def payment_successful(order_id: str, payment_id: str, payment_signature: str):
    redirect = verify_payment(order_id, payment_id, payment_signature)
    order_details = get_order_details(order_id)
    cart_details = get_order_details(order_id)["notes"]
    Orders(user_id=cart_details["user_id"], order_id=order_id)
    Cart(user_id=cart_details["user_id"]).clear_cart()
    Cart(cart_details["user_id"]).create_order_from_cart()
    if redirect:
        Payments(
            order_id=order_id,
            payment_id=payment_id,
            payment_amount=order_details["amount"],
            payment_status=order_details["status"],
            payment_method="razorpay",
            payment_timestamp=order_details["created_at"],
        )
        return RedirectResponse(url="http://localhost:3000")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed"
        )
