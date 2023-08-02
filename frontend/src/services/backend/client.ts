import { useCookies } from "@vueuse/integrations/useCookies";
import axios from "axios";
import type { AxiosInstance, AxiosResponse } from "axios";

export interface ApiRequestInstance {
    get<T>(url: string, data?: unknown): Promise<RequestResponse<T>>;
    post<T>(url: string, data: unknown): Promise<RequestResponse<T>>;
    put<T, U = T>(url: string, data: U): Promise<RequestResponse<T>>;
    patch<T, U = Partial<T>>(url: string, data: U): Promise<RequestResponse<T>>;
    delete<T>(url: string): Promise<RequestResponse<T>>;
}

export interface RequestResponse<T> {
    response: AxiosResponse<T> | null;
    data: T | null;
    error: any;
}

const request = {
    async safe<T, U>(
    funcCall: (url: string, data: U) => Promise<AxiosResponse<T>>,
        url: string,
        data: U
    ): Promise<RequestResponse<T>> {
        let error = null;
        const response = await funcCall(url, data).catch(function (e) {
            console.log(e);
            // Insert Generic Error Handling Here
            error = e;
            return null;
        });
        return { response, error, data: response?.data ?? null };
    },
};

function getRequests(axiosInstance: AxiosInstance): ApiRequestInstance {
    return {
        async get<T>(url: string, params = {}): Promise<RequestResponse<T>> {
            let error = null;
            const response = await axiosInstance.get<T>(url, params).catch((e) => {
                error = e;
            });
            if (response != null) {
                return { response, error, data: response?.data };
            }
            return { response: null, error, data: null };
        },

        async post<T, U>(url: string, data: U) {
            // eslint-disable-next-line @typescript-eslint/unbound-method
            return await request.safe<T, U>(axiosInstance.post, url, data);
        },

        async put<T, U = T>(url: string, data: U) {
            // eslint-disable-next-line @typescript-eslint/unbound-method
            return await request.safe<T, U>(axiosInstance.put, url, data);
        },

        async patch<T, U = Partial<T>>(url: string, data: U) {
            // eslint-disable-next-line @typescript-eslint/unbound-method
            return await request.safe<T, U>(axiosInstance.patch, url, data);
        },

        async delete<T>(url: string) {
            // eslint-disable-next-line @typescript-eslint/unbound-method
            return await request.safe<T, undefined>(axiosInstance.delete, url, undefined);
        },
    };
}

export const access_token_cookie = "mediamanager.auth.access_token";
export const useApi = function (): ApiRequestInstance {
    const cookies = useCookies();
    const axiosInstance = axios.create({
        headers: {
            Accept: 'application/json',
        }
    });

    // set auth header before each request
    axiosInstance.interceptors.request.use( (config) => {
        config.headers["Authorization"] = cookies.get(access_token_cookie) || "";
        return config;
    })

    const requests = getRequests(axiosInstance);
    return requests;
}
