
/**	@file       mian.cpp
 *	@note       Hikvision Digital Technology Co., Ltd. All Right Reserved.
 *	@brief		 
 *
 *	@author     lipengfei
 *	@date       2018/05/10
 *	@note       ��ʷ��¼��
 *	@note       V1.0.0  
 *	@warning	
 */


#include <stdlib.h>
#include <stdio.h>
#include "OSSocket.h"
#include "JsonParse.h"
#include "CmdParse.h"
#include <vector>
#include <climits>
#include <iostream>
#include <algorithm>
#include <cmath>
#define inf 1000000000
#define MAX_SOCKET_BUFFER       (1024 * 1024 * 4)       /// ���ͽ����������4M
using namespace std;


/** @fn     int RecvJuderData(OS_SOCKET hSocket, char *pBuffer)
 *  @brief	��������
 *	@param  -I   - OS_SOCKET hSocket
 *	@param  -I   - char * pBuffer
 *	@return int
 */
// ����1��123.56.24.163���ǲ��з�������IP��
// ����2��32210���ǲ��з��������������ӵĶ˿ڡ�
// ����3��e05ebb7d-84cb-4f20-952e-720b08c97529���Ǳ������е����ơ�
// ./main.exe 123.56.24.163 30301 03007105-159b-4027-8edb-dcd8e5c95eeb
int RecvJuderData(OS_SOCKET hSocket, char *pBuffer)
{
    int         nRecvLen = 0;
    int         nLen = 0;

    while (1)
    {
        // ����ͷ������
        nLen = OSRecv(hSocket, pBuffer + nRecvLen, MAX_SOCKET_BUFFER);
        if (nLen <= 0)
        {
            printf("recv error\n");
            return nLen;
        }

        nRecvLen += nLen;

        if (nRecvLen >= SOCKET_HEAD_LEN)
        {
            break;
        }
    }

    int         nJsonLen = 0;
    char        szLen[10] = { 0 };

    memcpy(szLen, pBuffer, SOCKET_HEAD_LEN);

    nJsonLen = atoi(szLen);

    while (nRecvLen < (SOCKET_HEAD_LEN + nJsonLen))
    {
        // ˵�����ݻ�û������
        nLen = OSRecv(hSocket, pBuffer + nRecvLen, MAX_SOCKET_BUFFER);
        if (nLen <= 0)
        {
            printf("recv error\n");
            return nLen;
        }

        nRecvLen += nLen;
    }
    //printf("%s",pBuffer);
    return 0;
}

/** @fn     int SendJuderData(OS_SOCKET hSocket, char *pBuffer, int nLen)
 *  @brief	��������
 *	@param  -I   - OS_SOCKET hSocket
 *	@param  -I   - char * pBuffer
 *	@param  -I   - int nLen
 *	@return int
 */
int SendJuderData(OS_SOCKET hSocket, char *pBuffer, int nLen)
{
    int     nSendLen = 0;
    int     nLenTmp = 0;

    while (nSendLen < nLen)
    {
        nLenTmp = OSSend(hSocket, pBuffer + nSendLen, nLen - nSendLen);
        if (nLenTmp < 0)
        {
            return -1;
        }

        nSendLen += nLenTmp;
    }

    return 0;
}


/** @fn     void AlgorithmCalculationFun()
 *  @brief	ѧ�����㷨���㣬 ����ʲô�Ķ��Լ�д��
 *	@return void
 */
typedef struct UAV_RECORD
    {
        int uavno;
        int goodno;
        int endcoor[2];
        bool upwithnogood;
        bool togetgood;
        bool downtogetgood;
        bool upwithgood;
        bool toputgood;
        bool downtoputgood;
        UAV_RECORD()
        {
         fill_n(endcoor,2,-1);
         uavno = -1;
         goodno = -1;
         upwithnogood = true;
         togetgood = false;
         downtogetgood = false;
         upwithgood = false;
         toputgood = false;
         downtoputgood = false;
        }
    }uavrecord;
void  AlgorithmCalculationFun(MAP_INFO *pstMap, MATCH_STATUS * pstMatch, FLAY_PLANE *pstFlayPlane,vector<uavrecord> &uavs)
{
    int flylow = pstMap->nHLow;
    vector<int> z_status;
    for(int uavindex=0;uavindex<(pstMatch->nUavWeNum);++uavindex)
    {
        z_status.push_back(pstMatch->astWeUav[uavindex].nZ);
    }
    vector<UAV>myuav(pstMatch->astWeUav,(pstMatch->astWeUav)+(pstMatch->nUavWeNum));
    for(int i=0;i<(pstMatch->nUavWeNum);++i)
    {

        //���¼���ķɻ���������
        if(int (uavs.size())<=(i+1))
        {
            uavrecord tempuav;
            uavs.push_back(tempuav);
        }
        if(pstMatch->astWeUav[i].nStatus == 1)
        {
            continue;
        }
        int pstshouldindex = -1;
        for(int pstindex = 0;pstindex<pstFlayPlane->nUavNum;pstindex++)
        {
            if(i == pstFlayPlane->astUav[pstindex].nNO)
            {
               pstshouldindex = pstindex;
               break;
            }
        }
        if(uavs[i].upwithnogood)
        {
            //vector<int>::iterator it;
            auto it = find(z_status.begin(),z_status.end(),(myuav[i].nZ)+1);
            if (it==z_status.end())
            {   
                pstFlayPlane->astUav[pstshouldindex].nZ += 1; 
                z_status[i] += 1;
            }
            if(pstFlayPlane->astUav[pstshouldindex].nZ > flylow)
            {
                uavs[i].upwithnogood = false;
                uavs[i].togetgood = true;
            }
        }
        else if(uavs[i].togetgood)
        {
            //ɾ���Ѿ���׷�ٵ�goodno
            vector<int>goodnolist;
            for(uavrecord goodin:uavs)
            {
            goodnolist.push_back(goodin.goodno);
            }
            vector<GOODS>goodinfo(pstMatch->astGoods,(pstMatch->astGoods)+(pstMatch->nGoodsNum));
            for(int initgoodno:goodnolist)
            {
               for(auto k = goodinfo.begin();k != goodinfo.end();k++)
               {
                   if(initgoodno == (*k).nNO && (uavs[i].goodno != (*k).nNO))
                   {
                       goodinfo.erase(k);
                       break;
                   }
               }
            }
            int goodnum = goodinfo.size();
            if(goodnum > 0)
            {
                vector<int> dis_start;
                for(int goodindex =0;goodindex<goodnum;goodindex++)
                {
                if(myuav[i].nLoadWeight >= goodinfo[goodindex].nWeight)
                {
                    int oushidis = pow((goodinfo[goodindex].nStartX - myuav[i].nX),2)+\
                            pow((goodinfo[goodindex].nStartY - myuav[i].nY),2)+\
                            pow(myuav[i].nZ,2);
                    dis_start.push_back(oushidis);
                }
                else
                {
                    dis_start.push_back(1000000000);
                }
                }
                //vector<int>::iterator min = min_element(dis_start.begin(), dis_start.end());
                
                auto min = min_element(dis_start.begin(), dis_start.end());
                int min_index = distance(dis_start.begin(),min);
                if(dis_start[min_index] == 1000000000)
                {
                    continue;
                }
                z_status[i] = -1;
                uavs[i].goodno = goodinfo[min_index].nNO;
                goodnolist[i] = goodinfo[min_index].nNO;
                int dis_x = goodinfo[min_index].nStartX - myuav[i].nX;
                int dis_y = goodinfo[min_index].nStartY - myuav[i].nY;
                if(dis_x != 0)
                {
                    pstFlayPlane->astUav[pstshouldindex].nX += int(dis_x/abs(dis_x));
                }
                if(dis_y != 0)
                {
                    pstFlayPlane->astUav[pstshouldindex].nY += int(dis_y/abs(dis_y));
                }
                if(dis_x==0 && dis_y == 0)
                {
                    uavs[i].endcoor[0] = goodinfo[min_index].nEndX;
                    uavs[i].endcoor[1] = goodinfo[min_index].nEndY;
                    pstFlayPlane->astUav[pstshouldindex].nZ --;
                    uavs[i].togetgood = false;
                    uavs[i].downtogetgood = true;                     
                }
            }
            else 
            {
                continue;
            }
            
        }
        else if(uavs[i].downtogetgood)
        {
            if(pstFlayPlane->astUav[pstshouldindex].nZ == 0)
            {
                pstFlayPlane->astUav[pstshouldindex].nGoodsNo = uavs[i].goodno;
                uavs[i].downtogetgood = false;
                uavs[i].upwithgood = true;
            }
            else
            {
                pstFlayPlane->astUav[pstshouldindex].nZ --;
            }
        }
        else if(uavs[i].upwithgood)
        {
            pstFlayPlane->astUav[pstshouldindex].nZ ++;
            if(pstFlayPlane->astUav[pstshouldindex].nZ>flylow)
            {
                uavs[i].upwithgood = false;
                uavs[i].toputgood = true;
            }
        }
        else if(uavs[i].toputgood)
        {
            int dis_end_x = uavs[i].endcoor[0] - pstFlayPlane->astUav[pstshouldindex].nX;
            int dis_end_y = uavs[i].endcoor[1] - pstFlayPlane->astUav[pstshouldindex].nY;
            if(dis_end_x != 0)
            {
                pstFlayPlane->astUav[pstshouldindex].nX += int(dis_end_x/abs(dis_end_x));
            }
            if(dis_end_y != 0)
            {
                pstFlayPlane->astUav[pstshouldindex].nY += int(dis_end_y/abs(dis_end_y));
            }
            if(dis_end_x==0 && dis_end_y == 0)
            {
                uavs[i].toputgood = false;
                uavs[i].downtoputgood = true;                     
            }
        }
        else if(uavs[i].downtoputgood)
        {
            if(pstFlayPlane->astUav[pstshouldindex].nZ == 0)
            {
                pstFlayPlane->astUav[pstshouldindex].nGoodsNo = -1;
                uavs[i].downtoputgood = false;
                uavs[i].upwithnogood = true;
            }
            else 
            {
                pstFlayPlane->astUav[pstshouldindex].nZ -- ;
            }
        }
 
    }
    int len = pstMatch->nUavWeNum;
    for(int flyplayindex= len - 1;flyplayindex >=0;flyplayindex--)
    {
        if(myuav[flyplayindex].nStatus == 1)
        {
            for (int i = flyplayindex; i < pstFlayPlane->nUavNum; i++)
            {
                if(myuav[flyplayindex].nNO == pstFlayPlane->astUav[i].nNO)
                {
                    for(int j = i;j<pstFlayPlane->nUavNum;j++)
                    {
                        pstFlayPlane ->astUav[j] = pstFlayPlane ->astUav[j+1];
                    }
                    
                    pstFlayPlane->nUavNum --; 
                }
            }

        }
    }
    //printf("num:%d\n",pstFlayPlane->nUavNum);
    // for(int i=0;i<len;i++)
    // {
    //     for(int j=i;j<len;j++)
    //     {
    //         if(myuav[j].nStatus !=1 )
    //         {
    //             UAV tempuav = pstFlayPlane->astUav[i];

    //             UAV tempvecuav = myuav[i];
    //             myuav[i] = myuav[j];
    //             myuav[j] = tempvecuav;
    //             pstFlayPlane->astUav[i] =  pstFlayPlane->astUav[j];
    //             pstFlayPlane->astUav[j] = tempuav;
    //             break;

    //         }
    //         else 
    //         {
    //             pstFlayPlane->nUavNum --;
    //             continue;
    //         }
    //     }
    // }
}



int main(int argc, char *argv[])
{
#ifdef OS_WINDOWS
    // windows�£���Ҫ���г�ʼ������
    WSADATA wsa;
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0)
    {
        printf("WSAStartup failed\n");
        return false;
    }

#endif

    char        szIp[64] = { 0 };
    int         nPort = 0;
    char        szToken[128] = { 0 };
    int         nRet = 0;
    OS_SOCKET   hSocket;
    char        *pRecvBuffer = NULL;
    char        *pSendBuffer = NULL;
    int         nLen = 0;
   
        // ���ص���ȥ�����
    if (argc != 4)
    {
        printf("error arg num\n");
        return -1;
    }

    // ��������
    strcpy(szIp, argv[1]);
    nPort = atoi(argv[2]);
    strcpy(szToken, argv[3]);

//     strcpy(szIp, "39.106.111.130");
//     nPort = 4010;
//     strcpy(szToken, "36d0a20b-7fab-4a93-b7e4-3247533b903a");

    printf("server ip %s, prot %d, token %s\n", szIp, nPort, szToken);

    // ��ʼ���ӷ�����
    nRet = OSCreateSocket(szIp, (unsigned int)nPort, &hSocket);
    if (nRet != 0)
    {
        printf("connect server error\n");
        return nRet;
    }

    // ������ܷ����ڴ�
    pRecvBuffer = (char*)malloc(MAX_SOCKET_BUFFER);
    if (pRecvBuffer == NULL)
    {
        return -1;
    }

    pSendBuffer = (char*)malloc(MAX_SOCKET_BUFFER);
    if (pSendBuffer == NULL)
    {
        free(pRecvBuffer);
        return -1;
    }

    memset(pRecvBuffer, 0, MAX_SOCKET_BUFFER);

    // ��������  ���ӳɹ���Judger�᷵��һ����Ϣ��
    nRet = RecvJuderData(hSocket, pRecvBuffer);
    if (nRet != 0)
    {
        return nRet;
    }

    // json ����
    // ��ȡͷ��
    CONNECT_NOTICE  stNotice;

    nRet = ParserConnect(pRecvBuffer + SOCKET_HEAD_LEN, &stNotice);
    if (nRet != 0)
    {
        return nRet;
    }

    // ���ɱ�����ݵ�json
    TOKEN_INFO  stToken;

    strcpy(stToken.szToken, szToken);  // ����ǵ��Խ׶Σ�����������Ե�token�����ҵĶ�ս�л�ȡ��
                                       // ʵ�ʱ�������Ҫ������Եģ�����demoд�ģ��з��������ô��롣
    strcpy(stToken.szAction, "sendtoken");

    memset(pSendBuffer, 0, MAX_SOCKET_BUFFER);
    nRet = CreateTokenInfo(&stToken, pSendBuffer, &nLen);
    if (nRet != 0)
    {
        return nRet;
    }
    // ѡ������з������������(Player -> Judger)
    nRet = SendJuderData(hSocket, pSendBuffer, nLen);
    if (nRet != 0)
    {
        return nRet;
    }

    //�����֤���(Judger -> Player)��
    memset(pRecvBuffer, 0, MAX_SOCKET_BUFFER);
    nRet = RecvJuderData(hSocket, pRecvBuffer);
    if (nRet != 0)
    {
        return nRet;
    }

    // ������֤�����json
    TOKEN_RESULT      stResult;
    nRet = ParserTokenResult(pRecvBuffer + SOCKET_HEAD_LEN, &stResult);
    if (nRet != 0)
    {
        return 0;
    }

    // �Ƿ���֤�ɹ�
    if (stResult.nResult != 0)
    {
        printf("token check error\n");
        return -1;
    }
    // ѡ������з����������Լ���׼������(Player -> Judger)
    READY_PARAM     stReady;

    strcpy(stReady.szToken, szToken);
    strcpy(stReady.szAction, "ready");

    memset(pSendBuffer, 0, MAX_SOCKET_BUFFER);
    nRet = CreateReadyParam(&stReady, pSendBuffer, &nLen);
    if (nRet != 0)
    {
        return nRet;
    }
    nRet = SendJuderData(hSocket, pSendBuffer, nLen);
    if (nRet != 0)
    {
        return nRet;
    }

    //��ս��ʼ֪ͨ(Judger -> Player)�� 
    memset(pRecvBuffer, 0, MAX_SOCKET_BUFFER);
    nRet = RecvJuderData(hSocket, pRecvBuffer);
    if (nRet != 0)
    {
        return nRet;
    }
    // ��������
    //Mapinfo �ṹ����ܴܺ󣬲�̫�ʺϷ���ջ�У����Զ���Ϊȫ�ֻ����ڴ����
    MAP_INFO            *pstMapInfo;
    MATCH_STATUS        *pstMatchStatus;
    FLAY_PLANE          *pstFlayPlane;

    pstMapInfo = (MAP_INFO *)malloc(sizeof(MAP_INFO));
    if (pstMapInfo == NULL)
    {
        return -1;
    }

    pstMatchStatus = (MATCH_STATUS *)malloc(sizeof(MATCH_STATUS));
    if (pstMapInfo == NULL)
    {
        return -1;
    }

    pstFlayPlane = (FLAY_PLANE *)malloc(sizeof(FLAY_PLANE));
    if (pstFlayPlane == NULL)
    {
        return -1;
    }

    memset(pstMapInfo, 0, sizeof(MAP_INFO));
    memset(pstMatchStatus, 0, sizeof(MATCH_STATUS));
    memset(pstFlayPlane, 0, sizeof(FLAY_PLANE));

    nRet = ParserMapInfo(pRecvBuffer + SOCKET_HEAD_LEN, pstMapInfo);
    if (nRet != 0)
    {
        return nRet;
    }

    // ��һ�ΰ����˻��ĳ�ʼ��ֵ��flayplane
    pstFlayPlane->nPurchaseNum = 0;
    pstFlayPlane->nUavNum = pstMapInfo->nUavNum;
    for (int i = 0; i < pstMapInfo->nUavNum; i++)
    {
        pstFlayPlane->astUav[i] = pstMapInfo->astUav[i];
    }

    // ���ݷ�����ָ���ͣ�Ľ��ܷ�������
    //����һ�����˻���������
    vector<uavrecord>uavs;
    UAV *inituav = pstFlayPlane ->astUav;
    for(; inituav->nGoodsNo != 0; inituav++)
    {
        uavrecord uavinit;
        uavs.push_back(uavinit);
    }
    
    while (1)
    {
        // ���е�ǰʱ�̵����ݼ���, �����мƻ��ṹ�壬ע�⣺0ʱ�̲��ܽ����ƶ�������һ�ν����ѭ��ʱ
        if (pstMatchStatus->nTime != 0)
        {
            AlgorithmCalculationFun(pstMapInfo, pstMatchStatus, pstFlayPlane,uavs);
        }

        
        //���ͷ��мƻ��ṹ��
        memset(pSendBuffer, 0, MAX_SOCKET_BUFFER);
        nRet = CreateFlayPlane(pstFlayPlane, szToken, pSendBuffer, &nLen);
        if (nRet != 0)
        {
            return nRet;
        }
        nRet = SendJuderData(hSocket, pSendBuffer, nLen);
        if (nRet != 0)
        {
            return nRet;
        }

        //printf("%s\n", pSendBuffer);
        printf("current time :%d\n",pstMatchStatus->nTime);
        // ���ܵ�ǰ����״̬
        memset(pRecvBuffer, 0, MAX_SOCKET_BUFFER);
        nRet = RecvJuderData(hSocket, pRecvBuffer);
        if (nRet != 0)
        {
            return nRet;
        }
        

        // ����
        nRet = ParserMatchStatus(pRecvBuffer + SOCKET_HEAD_LEN, pstMatchStatus);
        if (nRet != 0)
        {
            return nRet;
        }

        if (pstMatchStatus->nMacthStatus == 1)
        {
            // ��������
            printf("game over, we value %d, enemy value %d\n", pstMatchStatus->nWeValue, pstMatchStatus->nEnemyValue);
            return 0;
        }
    }

    // �ر�socket
    OSCloseSocket(hSocket);
    // ��Դ����
    free(pRecvBuffer);
    free(pSendBuffer);
    free(pstMapInfo);
    free(pstMatchStatus);
    free(pstFlayPlane);

    return 0;
}