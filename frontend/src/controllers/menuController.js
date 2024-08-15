import { SERVER_URL } from "../setup";

const getMenu = async (token) => {
  try {
    console.log("Menu URL: " + SERVER_URL + "/kitchen/menu");
    const res = await fetch(SERVER_URL + "/kitchen/menu", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    console.log("SUCCESS");
    if (res.ok) {
      data.forEach(element => {
        element.selected = false;
      });
      return data;
    } else {
      console.log(data);
    }
  } catch (err) {
    console.log(err);
  }
};

export { getMenu };
